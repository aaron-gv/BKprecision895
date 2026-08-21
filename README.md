# BKPrecision895

Python-based tool for communicating with the **B&K Precision 895 LCR Meter** and performing automated LCR frequency sweeps.

The application uses **PyVISA** to communicate with the instrument through USB and provides a graphical interface for configuring and running measurements.

The program can perform:

- Parallel capacitance / resistance measurements (**CP / RP**)
- Series capacitance / resistance measurements (**CS / RS**)
- Linear or logarithmic frequency sweeps
- Multiple measurement cycles
- Configurable waiting time between frequencies
- Automatic TXT data export
- Automatic Excel `.xlsx` generation
- Automatic capacitance and resistance graphs

---

# 1. Requirements

Before using this project, make sure you have:

- Windows
- Python 3
- B&K Precision 895 LCR Meter
- USB cable
- NI-VISA
- The Python packages required by this project

---

# 2. Install Python

Install **Python 3** on your computer.

Download Python from the official Python website:

https://www.python.org/downloads/

During the installation, make sure to enable:

**Add Python to PATH**

Then finish the installation.

To verify that Python is installed, open **Command Prompt (CMD)** and run:

```cmd
python --version
