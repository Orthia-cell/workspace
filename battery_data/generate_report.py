#!/usr/bin/env python3
"""
Generate Battery Monitor Report from CSV data
"""

import csv
import os
from datetime import datetime, timedelta
from pathlib import Path

CSV_FILE = "/root/.openclaw/workspace/battery_data/voltage_log.csv"
REPORT_FILE = "/root/.openclaw/workspace/battery_data/latest_report.txt"

# Alert thresholds
ALERT_LOW = 13.0
ALERT_HIGH = 15.2

def load_voltage_data():
    """Load all voltage data from CSV"""
    data = []
    try:
        with open(CSV_FILE, 'r') as f:
            reader = csv.reader(f)
            header = next(reader, None)  # Skip header
            for row in reader:
                if len(row) >= 2:
                    try:
                        timestamp = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
                        voltage = float(row[1])
                        data.append({'timestamp': timestamp, 'voltage': voltage})
                    except:
                        continue
    except Exception as e:
        print(f"Error reading CSV: {e}")
    return data

def get_24h_stats(data, now):
    """Get 24-hour statistics"""
    cutoff = now - timedelta(hours=24)
    recent = [d for d in data if d['timestamp'] >= cutoff]
    
    if not recent:
        return None, None, None, 0
    
    voltages = [d['voltage'] for d in recent]
    return min(voltages), max(voltages), sum(voltages)/len(voltages), len(voltages)

def main():
    now = datetime.now()
    data = load_voltage_data()
    
    if not data:
        print("No data available")
        return 1
    
    current = data[-1]
    current_voltage = current['voltage']
    current_time = current['timestamp']
    
    min_24h, max_24h, avg_24h, count_24h = get_24h_stats(data, now)
    
    # Check alerts
    alert_status = "✅ NORMAL"
    alert_detail = "Voltage within normal range"
    
    if current_voltage < ALERT_LOW:
        alert_status = "⚠️  LOW VOLTAGE ALERT"
        alert_detail = f"Current: {current_voltage:.3f}V < {ALERT_LOW:.1f}V"
    elif current_voltage > ALERT_HIGH:
        alert_status = "⚠️  HIGH VOLTAGE ALERT"
        alert_detail = f"Current: {current_voltage:.3f}V > {ALERT_HIGH:.1f}V"
    
    # Generate report
    report = []
    report.append("╔" + "═" * 62 + "╗")
    report.append("║" + " " * 14 + "ARDUINO IOT BATTERY MONITOR REPORT" + " " * 15 + "║")
    report.append("╠" + "═" * 62 + "╣")
    report.append(f"║  Thing: Load Tester_2 (37cd8c67-7ebf-401f-a88e-321c9a285c4a) ║")
    report.append(f"║  Property: TBL3 (Voltage)                                  ║")
    report.append(f"║  Report Time: {now.strftime('%Y-%m-%d %H:%M:%S'):<46} ║")
    report.append("╠" + "═" * 62 + "╣")
    report.append("║  CURRENT READING                                           ║")
    report.append("║  " + "─" * 56 + "   ║")
    report.append(f"║  Voltage:     {current_voltage:.3f} V{'':<36} ║")
    report.append(f"║  Timestamp:   {current_time.strftime('%Y-%m-%d %H:%M:%S'):<46} ║")
    report.append(f"║  Status:      {alert_status:<46} ║")
    report.append("╠" + "═" * 62 + "╣")
    report.append(f"║  24-HOUR STATISTICS ({count_24h} data points){'':<27} ║")
    report.append("║  " + "─" * 56 + "   ║")
    if min_24h is not None:
        report.append(f"║  Minimum:     {min_24h:.3f} V{'':<36} ║")
        report.append(f"║  Maximum:     {max_24h:.3f} V{'':<36} ║")
        report.append(f"║  Average:     {avg_24h:.3f} V{'':<36} ║")
        report.append(f"║  Range:       {max_24h - min_24h:.3f} V{'':<36} ║")
    else:
        report.append(f"║  (No historical data available){'':<31} ║")
    report.append("╠" + "═" * 62 + "╣")
    report.append("║  ALERT THRESHOLDS                                          ║")
    report.append("║  " + "─" * 56 + "   ║")
    report.append(f"║  Low Alert:   < {ALERT_LOW:.1f} V{'':<38} ║")
    report.append(f"║  High Alert:  > {ALERT_HIGH:.1f} V{'':<37} ║")
    report.append("╠" + "═" * 62 + "╣")
    report.append("║  ALERT STATUS                                              ║")
    report.append("║  " + "─" * 56 + "   ║")
    report.append(f"║  {alert_status:<58} ║")
    report.append(f"║  {alert_detail:<58} ║")
    report.append("╚" + "═" * 62 + "╝")
    report.append("")
    report.append(f"Data logged to: {CSV_FILE}")
    
    report_text = "\n".join(report)
    
    # Save report
    with open(REPORT_FILE, 'w') as f:
        f.write(report_text)
    
    print(report_text)
    return 0

if __name__ == "__main__":
    exit(main())
