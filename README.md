# BKPrecision895

Python-based tool for communicating with the **B&K Precision 895 LCR Meter** and performing automated LCR frequency sweeps.

The application uses **PyVISA** to communicate with the instrument through USB and provides a graphical interface for configuring and running measurements.

---

## 1. Requirements

Before using this project, make sure you have:

- Windows
- Python 3
- B&K Precision 895 LCR Meter
- USB connection between the computer and the instrument
- VISA implementation (NI-VISA)
- Required Python packages

---

## 2. Install Python

Install **Python 3** on your computer.

During installation, make sure to enable:

**Add Python to PATH**

After installation, open Command Prompt and check that Python is available:

```cmd
python --version
