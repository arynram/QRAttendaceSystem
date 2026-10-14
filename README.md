# 🏰 Clash of Clans QR Smart Attendance System ⚔️
### *With Real-Time FCFS vs Round Robin CPU Scheduling & Downloadable War Report PDF*

A gaming-themed attendance simulation built for college projects, featuring **Clash of Clans (CoC)** visual aesthetics, multi-class support, automated time-slot calculation, and instant **PDF War Reports**.

---

## 🎮 Clash of Clans (CoC) Theme Highlights
- **Town Hall Dark Stone Background**: Deep village stone base (`#11151A` - `#202731`) with golden trims (`#EAB308`).
- **Wooden Plank Cards & Gold Storage Badges**: Beveled village boards with glowing badges (`🟡 Gold`, `🔮 Dark Elixir`, `🛡️ Shield Active`).
- **3D Battle Buttons**: Green Battle Attack buttons (`⚔️ START CLAN ATTENDANCE WAR`) and Red Surrender buttons.
- **Shield Countdown**: 10-second village shield timer linked to dynamic QR token regeneration.

---

## 📚 Supported Subjects & Classes
- **Classes**:
  - `AIML A`
  - `AIML B`
  - `AIML C`
  - `AIML D`
- **Subjects**:
  - `PPCA` (Programming for Problem Solving with C / Advanced Programming)
  - `DSA` (Data Structures & Algorithms)
  - `COOS` (Computer Organization & Operating Systems)
  - `M-III` (Mathematics III)
  - `UHV-II` (Universal Human Values II)

---

## ⏰ Automated Time-Slot & Date Fetching
- **Date**: Automatically fetches today's date (`YYYY-MM-DD`) with full flexibility to change.
- **Smart 30-Minute Rounding**:
  - If a teacher starts a session around `03:25 PM`, the system rounds to the nearest 30-minute block (`03:30 PM`) and sets a default 1-hour slot: **`02:30 PM - 03:30 PM`**.
  - Teachers can customize both start and end times in the setup screen.

---

## 📜 Downloadable PDF War Report
- Once students mark attendance, the teacher receives an **Official Clan Attendance War Report (PDF)**:
  - Class Name (e.g., `AIML A`)
  - Subject (e.g., `COOS`)
  - Date & Lecture Time Slot
  - CPU Scheduling Algorithm (`Round Robin` vs `FCFS`)
  - Table of all present students with timestamps and verification status.

---

## 📂 Project Structure

```text
qr_attendance/
│
├── pdf_generator.py    # ReportLab PDF generator for Clan War Reports
├── scheduler.py        # CPU Scheduling Engine (FCFS & Round Robin algorithms + Gantt)
├── logic.py            # Business logic (Token generation, smart time-slot, request logging)
├── ui.py               # Clash of Clans UI (Custom CSS, Live QR, PDF Download, Gantt)
├── qr_code.py          # Dynamic QR code generation & Wi-Fi IP detection
├── csv_handler.py      # Attendance CSV read/write operations
│
├── app.py              # Main application launcher
├── attendance.csv      # CSV data storage
├── requirements.txt    # Dependencies (streamlit, qrcode, pillow, reportlab)
└── README.md           # Documentation
```

---

## 🚀 How to Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Application**:
   ```bash
   streamlit run app.py
   ```

3. **Access Links**:
   - **Teacher Dashboard (Laptop)**: [http://localhost:8501](http://localhost:8501)
   - **Student Scan (Mobile)**: `http://<laptop-ip>:8501`
