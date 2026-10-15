# ⚡ Smart QR Attendance System

A clean, real-time college attendance management system built with **Python** and **Streamlit**. Designed for college smartboards and mobile scanning, featuring dynamic rolling QR codes, session isolation, duplicate prevention, and instant PDF report generation.

---

## 🎯 Project Overview

This project provides an automated, contactless attendance solution for classrooms and lecture halls:
- **Faculty Portal (Smartboard / Laptop)**:
  - Secure 6-digit numeric PIN lock screen (`234567`).
  - Faculty profile for **Ms. Seema Nagrani** (Department of AIML).
  - Subject: **PPCA** (Class: `AIML C`).
  - Automated lecture slot detection using Indian Standard Time (IST, UTC+5:30) with nearest 30-minute rounding and 1-touch preset buttons.
  - Live rolling QR code display:
    - **Initial QR duration**: 20 seconds (allows students time to open their phone camera).
    - **Subsequent QR refreshes**: every 10 seconds.
  - Live counter of marked students with real-time roll numbers.
  - One-click **PDF Report Generation** and historical records download.

- **Student Attendance Screen (Mobile Browser)**:
  - Students scan the QR code projected on the smartboard.
  - The URL loads the attendance form on their mobile browser.
  - Built-in **20-second token grace period** to ensure students are not rejected due to network delay.
  - Validates roll numbers and prevents duplicate attendance submissions for the same lecture.

---

## 📂 Project Architecture

The codebase is organized into modular Python files, making it clean, easy to maintain, and simple to explain during academic viva:

| File | Purpose | Explanation for Evaluation |
|---|---|---|
| `app.py` | Main Entry Point | Initializes the CSV database and launches the Streamlit interface. |
| `config.py` | Configuration & Credentials | Stores faculty profiles, PINs, department details, and QR refresh duration settings. |
| `logic.py` | Core Business Logic | Manages session state, IST time slots, dynamic token countdowns, token verification, and duplicate checks. |
| `qr_code.py` | QR Generator & Network Discovery | Detects local Wi-Fi IP address and compiles PNG image bytes for the dynamic QR code. |
| `csv_handler.py` | Database Persistence Layer | Reads, writes, and filters attendance records in `attendance.csv` using clean Python file I/O. |
| `pdf_generator.py` | Official PDF Generator | Uses ReportLab to compile downloadable attendance reports with college branding, metadata, and verified roll lists. |
| `ip_security.py` | Security & Anti-Proxy Module | Contains IP detection, 1-device-per-lecture restriction, and proxy/VPN checks (toggleable for demonstrations). |
| `ui.py` | Streamlit User Interface | Pure basic HTML elements, touch keypad, live dynamic QR countdown, and responsive student mobile forms. |

---

## 🚀 How to Run Locally

### 1. Requirements
Ensure you have Python 3.10+ installed. Install the dependencies:
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
Double-click **`run_attendance.bat`** or run:
```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

- **Teacher Smartboard / Laptop Portal**: Open `http://localhost:8501`
- **Faculty PIN Code**: `234567` (Ms. Seema Nagrani - PPCA)
- **Student Mobile Access**: Connect phone to the same Wi-Fi / Hotspot and access `http://<LAPTOP_IP>:8501`
