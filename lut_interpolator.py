# lut_interpolator.py

import numpy as np
import pandas as pd
from scipy.interpolate import RBFInterpolator


class LUTInterpolator:
    """
    Interpolates ft, gmro, and Id/W (nidw) over:
        - gm_id (gm/Id)
        - VDS
        - length_nm

    Expected CSV structure (for each VDS and quantity):
        length_nm, ngm_id, nft   (for ft)
        length_nm, ngm_id, ngmro (for gmro)
        length_nm, ngm_id, nidw  (for Id/W)

    You call `load_vds_csvs` once per VDS (0.2, 0.4), then `build_interpolators()`.
    """

    def __init__(self, kernel: str = "thin_plate_spline", epsilon=None):
        self.kernel = kernel
        self.epsilon = epsilon

        # We expose canonical quantity names
        self.quantities = ["id_w", "gmro", "ft"]

        # data[quantity][vds] = DataFrame(gm_id, length_nm, value)
        self.data = {q: {} for q in self.quantities}
        # rbf[quantity][vds] = RBFInterpolator over (gm_id, length_nm)
        self.rbf = {q: {} for q in self.quantities}

        # Set of available channel lengths (from the CSVs)
        self.lengths = None

    # -------------------------
    # Internal helpers
    # -------------------------
    def _append_data(self, df: pd.DataFrame, vds: float,
                     quantity_col: str, quantity_name: str):
        """
        df has columns: length_nm, ngm_id, <quantity_col>.
        This normalizes them to: gm_id, length_nm, value.
        """
        df = df.copy()

        df.rename(
            columns={
                "length_nm": "length_nm",
                "ngm_id": "gm_id",
                quantity_col: "value",
            },
            inplace=True,
        )

        df = df[["gm_id", "length_nm", "value"]].dropna()
        vds = float(vds)

        if vds not in self.data[quantity_name]:
            self.data[quantity_name][vds] = df
        else:
            # Just in case you ever load in pieces for same VDS
            self.data[quantity_name][vds] = pd.concat(
                [self.data[quantity_name][vds], df], ignore_index=True
            )

    # -------------------------
    # Public: data loading
    # -------------------------
    def load_vds_csvs(self, vds: float,
                      ft_path: str = None,
                      gmro_path: str = None,
                      idw_path: str = None):
        """
        Load the three CSVs for a given VDS.

        Parameters
        ----------
        vds : float
            The VDS value of these CSVs (e.g. 0.2, 0.4).
        ft_path : str
            Path to nft_vs_ngm_id_with_length_XXX.csv 
        gmro_path : str
            Path to ngmro_vs_ngm_id_with_length_XXX.csv.
        idw_path : str
            Path to nidw_vs_ngm_id_with_length_XXX.csv.
        """

        # --- ft (nft) ---
        if ft_path is not None:
            df_ft = pd.read_csv(ft_path)
            # Column name is typically "nft"
            ft_col_candidates = [
                c for c in df_ft.columns if c.lower().endswith("ft")]
            if not ft_col_candidates:
                raise ValueError(f"Could not find ft column in {ft_path}")
            ft_col = ft_col_candidates[0]
            self._append_data(df_ft, vds, ft_col, "ft")

        # --- gmro (ngmro) ---
        if gmro_path is not None:
            df_gmro = pd.read_csv(gmro_path)
            gmro_col_candidates = [
                c for c in df_gmro.columns if "gmro" in c.lower()]
            if not gmro_col_candidates:
                raise ValueError(f"Could not find gmro column in {gmro_path}")
            gmro_col = gmro_col_candidates[0]
            self._append_data(df_gmro, vds, gmro_col, "gmro")

        # --- Id/W (nidw) ---
        if idw_path is not None:
            df_idw = pd.read_csv(idw_path)
            idw_col_candidates = [
                c for c in df_idw.columns if "idw" in c.lower()]
            if not idw_col_candidates:
                raise ValueError(f"Could not find idw column in {idw_path}")
            idw_col = idw_col_candidates[0]
            self._append_data(df_idw, vds, idw_col, "id_w")

    # -------------------------
    # Build interpolators
    # -------------------------
    def build_interpolators(self):
        """
        Build 2D RBF interpolators for each quantity and each VDS:
            (gm_id, length_nm) -> value

        For intermediate VDS values, interpolation is done *afterwards*
        by linear interpolation between neighboring VDS planes.
        """
        self.rbf = {q: {} for q in self.quantities}
        all_lengths = set()

        for q in self.quantities:
            for vds, df in self.data[q].items():
                all_lengths.update(df["length_nm"].unique())

                X = df[["gm_id", "length_nm"]].values
                y = df["value"].values

                self.rbf[q][float(vds)] = RBFInterpolator(
                    X, y,
                    kernel=self.kernel,
                    epsilon=self.epsilon,
                )

        if all_lengths:
            self.lengths = sorted(int(L) for L in all_lengths)

    # -------------------------
    # Internal: VDS helper
    # -------------------------
    def _available_vds(self, quantity: str):
        return sorted(self.rbf[quantity].keys())

    def _interp_in_vds(self, quantity: str, gm_id: float,
                       vds: float, length_nm: float) -> float:
        """
        Core utility:
          - If vds exactly matches a loaded plane -> use that RBF.
          - Else -> linearly interpolate between the two neighboring planes.
          - Out-of-range vds is clamped to the nearest plane.
        """
        vds = float(vds)
        gm_id = float(gm_id)
        length_nm = float(length_nm)

        avail = self._available_vds(quantity)
        if not avail:
            raise ValueError(f"No interpolators for quantity '{quantity}'")

        # If we have an exact VDS plane:
        if vds in self.rbf[quantity]:
            f = self.rbf[quantity][vds]
            X = np.array([[gm_id, length_nm]])
            return float(f(X))

        # Below minimum -> clamp to lowest VDS
        if vds < avail[0]:
            f = self.rbf[quantity][avail[0]]
            X = np.array([[gm_id, length_nm]])
            return float(f(X))

        # Above maximum -> clamp to highest VDS
        if vds > avail[-1]:
            f = self.rbf[quantity][avail[-1]]
            X = np.array([[gm_id, length_nm]])
            return float(f(X))

        # Otherwise find bounding VDS values
        v1, v2 = None, None
        for i in range(len(avail) - 1):
            if avail[i] <= vds <= avail[i + 1]:
                v1, v2 = avail[i], avail[i + 1]
                break

        if v1 is None:
            # Fallback: should not happen, but just in case
            f = self.rbf[quantity][avail[-1]]
            X = np.array([[gm_id, length_nm]])
            return float(f(X))

        f1 = self.rbf[quantity][v1]
        f2 = self.rbf[quantity][v2]
        X = np.array([[gm_id, length_nm]])

        y1 = float(f1(X))
        y2 = float(f2(X))

        # Linear interpolation in VDS
        t = (vds - v1) / (v2 - v1)
        return y1 + t * (y2 - y1)

    # -------------------------
    # Public: forward prediction
    # -------------------------
    def predict(self, quantity: str, gm_id: float, vds: float, length_nm: float) -> float:
        """
        Predict a single quantity ("id_w", "gmro", or "ft") for given (gm_id, VDS, length_nm).
        """
        if quantity not in self.quantities:
            raise ValueError(
                f"Unknown quantity '{quantity}', expected one of {self.quantities}")

        return self._interp_in_vds(quantity, gm_id, vds, length_nm)

    def predict_all(self, gm_id: float, vds: float, length_nm: float) -> dict:
        """
        Predict all three: Id/W, gmro, ft for given (gm_id, VDS, length_nm).
        Returns a dict: {"id_w": ..., "gmro": ..., "ft": ...}
        """
        return {
            "id_w": self.predict("id_w", gm_id, vds, length_nm),
            "gmro": self.predict("gmro", gm_id, vds, length_nm),
            "ft":   self.predict("ft",   gm_id, vds, length_nm),
        }

    def estimate_length_from_gmro(self, gm_id: float, gmro_measured: float, vds: float,
                                  return_continuous: bool = False):
        """
        Given gm/Id, gmro and VDS, estimate the length using the raw gmro CSV data.

        Algorithm:
          1. Snap VDS to the closest gmro plane (0.2, 0.4, ...).
          2. For each discrete L, interpolate gmro(gm_id, L) along gm_id
             using the *raw* gmro vs gm/Id data at that VDS.
          3. Find adjacent lengths L1, L2 such that gmro_measured lies
             between gmro_pred(L1) and gmro_pred(L2).
          4. Optional: linearly interpolate to get continuous L*.
          5. Return discrete length = max(L1, L2) (your rule).

        If no such bracket is found (out of range), fall back to the
        length whose gmro_pred(L) is closest to gmro_measured.
        """
        if not self.data["gmro"]:
            raise ValueError(
                "gmro data not available. Load gmro CSVs with load_vds_csvs() and call build_interpolators()."
            )
        if self.lengths is None:
            raise ValueError(
                "No length information available. Did you call build_interpolators()?")

        gm_id = float(gm_id)
        gmro_measured = float(gmro_measured)
        vds_req = float(vds)

        # --- 1) choose nearest VDS plane using RAW gmro data ---
        avail_vds = sorted(self.data["gmro"].keys())
        vds_plane = min(avail_vds, key=lambda x: abs(x - vds_req))

        df_plane = self.data["gmro"][vds_plane]

        # --- 2) interpolate gmro along gm/id for each length ---
        gmro_pred = {}  # L -> gmro_pred

        for L in self.lengths:
            df_L = df_plane[df_plane["length_nm"] == L]
            if df_L.empty:
                continue

            df_L = df_L.sort_values("gm_id")
            gmids = df_L["gm_id"].values
            vals = df_L["value"].values

            # 1D linear interpolation in gm_id
            gmro_L = float(np.interp(gm_id, gmids, vals))
            gmro_pred[L] = gmro_L

        if not gmro_pred:
            raise ValueError(
                f"No gmro data available at VDS={vds_plane} for any length.")

        # Ensure ordered by length
        lengths_ordered = sorted(gmro_pred.keys())

        # --- 3) find bracket L1, L2 where gmro_measured lies between gmro_pred ---
        L_est = None
        L_disc = None
        bracket_found = False

        for i in range(len(lengths_ordered) - 1):
            L1 = lengths_ordered[i]
            L2 = lengths_ordered[i + 1]
            g1 = gmro_pred[L1]
            g2 = gmro_pred[L2]

            # Check if gmro_measured lies between g1 and g2 (any order)
            if (g1 <= gmro_measured <= g2) or (g2 <= gmro_measured <= g1):
                bracket_found = True

                # --- 4) continuous L* by linear interpolation between (L1,g1) and (L2,g2) ---
                if abs(g2 - g1) < 1e-12:
                    # essentially flat; take midpoint
                    L_est = 0.5 * (L1 + L2)
                else:
                    t = (gmro_measured - g1) / (g2 - g1)
                    L_est = L1 + t * (L2 - L1)

                # --- 5) discrete length per your rule = max(L1, L2) ---
                L_disc = max(L1, L2)
                break

        # --- no bracket found: fall back to nearest gmro_pred ---
        if not bracket_found:
            L_disc = min(lengths_ordered, key=lambda L: abs(
                gmro_pred[L] - gmro_measured))
            if L_est is None:
                L_est = float(L_disc)

        if return_continuous:
            return L_est, L_disc
        return L_disc
