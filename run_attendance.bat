@echo off
title Smart Attendance System - Prof. Deepthi Rapeti
cd /d "%~dp0"
echo Starting Smart Attendance System locally...
start http://localhost:8501
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
pause
