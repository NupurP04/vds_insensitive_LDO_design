# main.py

from lut_interpolator import LUTInterpolator

# Create LUT object
lut = LUTInterpolator()

# -------------------------
# Load all VDS planes
# -------------------------


# THIS IS FOR NMOS
# VDS = 0.2 V
lut.load_vds_csvs(
    vds=0.2,
    ft_path="/nmos/nft_vs_ngm_id_with_length_0p2V.csv",
    gmro_path="/nmos/ngmro_vs_ngm_id_with_length_0p2V.csv",
    idw_path="/nmos/nidw_vs_ngm_id_with_length_0p2V.csv",
)

# VDS = 0.4 V  (update these file names to your actual ones)
lut.load_vds_csvs(
    vds=0.4,
    ft_path="/nmos/nft_vs_ngm_id_with_length.csv",
    gmro_path="/nmos/ngmro_vs_ngm_id_with_length.csv",
    idw_path="/nmos/nidw_vs_ngm_id_with_length.csv",
)

# VDS = 1.8 V  (update these file names to your actual ones)
lut.load_vds_csvs(
    vds=0.8,
    ft_path="/nmos/nft_vs_ngm_id_with_length_1p8V.csv",
    gmro_path="/nmos/ngmro_vs_ngm_id_with_length_1p8V.csv",

    idw_path="/nmos/nidw_vs_ngm_id_with_length_1p8V.csv",
)

#  -------------------------------------------------------------
# THIS IS FOR PMOS
# VDS = 0.2 V
lut.load_vds_csvs(
    vds=0.2,
    ft_path="/pmos/nft_vs_ngm_id_with_length_0p2V.csv",
    gmro_path="/pmos/ngmro_vs_ngm_id_with_length_0p2V.csv",
    idw_path="/pmos/nidw_vs_ngm_id_with_length_0p2V.csv",
)

# VDS = 0.4 V  (update these file names to your actual ones)
lut.load_vds_csvs(
    vds=0.4,
    ft_path="/pmos/nft_vs_ngm_id_with_length.csv",
    gmro_path="/pmos/ngmro_vs_ngm_id_with_length.csv",
    idw_path="/pmos/nidw_vs_ngm_id_with_length.csv",
)

# VDS = 1.8 V  (update these file names to your actual ones)
lut.load_vds_csvs(
    vds=0.8,
    ft_path="/pmos/nft_vs_ngm_id_with_length_1p8V.csv",
    gmro_path="/pmos/ngmro_vs_ngm_id_with_length_1p8V.csv",
    idw_path="/pmos/nidw_vs_ngm_id_with_length_1p8V.csv",
)

# Build RBF interpolators
lut.build_interpolators()

print("Available channel lengths (nm):", lut.lengths)

# -------------------------
# Example 1: Forward prediction
# -------------------------

gm_id = 10.0      # example gm/Id
vds_query = 0.4   # example VDS between 0.4 V and 0.8 V
L_query = 720.0   # example length between 540 and 720

result = lut.predict_all(gm_id, vds_query, L_query)

print("\nForward prediction at gm/Id =", gm_id,
      ", VDS =", vds_query, "V, L =", L_query, "nm")
print("Id/W =", result["id_w"])
print("gmro =", result["gmro"])
print("ft   =", result["ft"])

# -------------------------
# Example 2: Estimate length from gmro + gm/Id + VDS
# -------------------------

gm_id_meas = 10.0      # gm/Id from measurement
gmro_meas = 35.0       # gmro from measurement
vds_meas = 0.4         # VDS at which you measured gmro

L_cont, L_disc = lut.estimate_length_from_gmro(
    gm_id_meas,
    gmro_meas,
    vds_meas,
    return_continuous=True,
)

print("\nLength estimation from gmro:")
print("Input: gm/Id =", gm_id_meas,
      ", gmro =", gmro_meas,
      ", VDS =", vds_meas, "V")
print("Estimated continuous L* (nm) =", L_cont)
print("Chosen discrete length (nm)  =", L_disc)  # uses your max(...) rule
