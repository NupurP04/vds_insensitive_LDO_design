# gm/Id Lookup Tables at Multiple VDS

This repository contains **gm/Id-based lookup tables (LUTs)** extracted from a **180 nm CMOS process** for both **NMOS and PMOS devices** at multiple drain–source voltages.

The LUTs are intended for **analog circuit design and device sizing**, particularly for applications where **VDS varies widely**, such as LDO pass devices.

---

##  Available LUTs

Lookup tables are provided at the following **VDS operating points**:

- **VDS = 0.2 V**
- **VDS = 0.4 V**
- **VDS = 1.8 V**

For **both NMOS and PMOS devices**.

---

##  LUT Contents

For each device type (NMOS / PMOS) and each VDS value, the following LUTs are included:

- **Id/W vs gm/Id vs Length**
- **gm·ro vs gm/Id vs Length**
- **fT vs gm/Id vs Length**

Each LUT is stored as a CSV file.

---

##  CSV File Format

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

##  Process Information

- **Technology node:** 180 nm CMOS  
- **Device types:** NMOS and PMOS  
- **Extraction:** Device-level simulations  
- **Bias condition:** Fixed VDS per LUT

---

##  Intended Use

These LUTs can be used for:
- gm/Id-based transistor sizing  
- Analog design exploration  
- VDS-aware device analysis  
- LDO and low-voltage analog design  

---

## 📄 Notes

- LUTs are extracted independently at each VDS value.
- Interpolation across VDS or length is **not included in this repository** at the moment.
- Data is intended for **design-space exploration and initial sizing**.

---

## 📜 License

For academic and research use.
