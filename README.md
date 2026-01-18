# gm/Id Lookup Tables and VDS Interpolation Framework

This repository contains:

1. **gm/Id-based lookup tables (LUTs)** extracted from a **180 nm CMOS process** for both **NMOS and PMOS devices** at multiple drain–source voltages, and  
2. A **Python-based interpolation framework** that enables prediction of device metrics at intermediate VDS and channel lengths.

The LUTs and interpolation engine are intended for **analog circuit design and device sizing**, particularly for applications where **VDS varies widely**, such as LDO pass devices.

---

## Available LUTs

Lookup tables are provided at the following **VDS operating points**:

- **VDS = 0.2 V**
- **VDS = 0.4 V**
- **VDS = 1.8 V**

For **both NMOS and PMOS devices**.

---

## LUT Contents

For each device type (NMOS / PMOS) and each VDS value, the following LUTs are included as CSV files:

- **Id/W vs gm/Id vs Length**
- **gm·ro vs gm/Id vs Length**
- **fT vs gm/Id vs Length**

---

## CSV File Format

All CSV files follow a consistent structure:

| Column Name | Description |
|------------|------------|
| `length_nm` | Channel length (nm) |
| `gm_id`     | gm/Id ratio |
| `idw` / `gmro` / `ft` | Corresponding device metric |

### Supported Channel Lengths
- 180 nm  
- 360 nm  
- 540 nm  
- 720 nm  
- 900 nm  
- 1080 nm  
- 1260 nm  

---

## Interpolation Framework

The repository also includes two Python files:

- `lut_interpolator.py` — Core interpolation engine  
- `main.py` — Example script demonstrating usage  

### What the interpolation does

The framework provides two key capabilities:

#### 1. Forward Prediction (gm/Id → Id/W, gmro, ft)

Given:
- gm/Id  
- VDS (can be intermediate, e.g., 0.5 V)  
- Channel length  

The code:
- Builds **Radial Basis Function (RBF) interpolators** on each VDS plane  
- Performs **linear interpolation across VDS planes**  
- Predicts:
  - Id/W  
  - gmro  
  - fT  

#### 2. Inverse Mapping: Length Estimation from gmro

Given:
- Measured gm/Id  
- Measured gmro  
- VDS  

The algorithm:
- Uses the **raw gmro vs gm/Id curves from the CSVs**
- Interpolates gmro at each discrete length  
- Finds the two lengths between which the measured gmro lies  
- Computes a continuous estimate  
- Returns the **larger of the two bounding lengths** as the final choice  
  (e.g., if the estimate lies between 540 nm and 720 nm → returns **720 nm**)

---

