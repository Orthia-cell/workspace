import requests
import json
import csv
import os
from datetime import datetime, timedelta

# Configuration
CONFIG_PATH = "/root/.openclaw/workspace/arduino-iot-pipeline/config/arduino_iot_config.json"
DATA_DIR = "/root/.openclaw/workspace/battery_data"
LOG_FILE = os.path.join(DATA_DIR, "voltage_log.csv")

# Thresholds
LOW_VOLTAGE_THRESHOLD = 13.0
HIGH_VOLTAGE_THRESHOLD = 15.2

def get_access_token(client_id, client_secret):
    """Get OAuth2 access token from Arduino IoT Cloud"""
    url = "https://api2.arduino.cc/iot/v1/clients/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": "https://api2.arduino.cc/iot"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    response = requests.post(url, data=payload, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]

def get_thing_property(token, thing_id, property_id):
    """Get current value of a thing property"""
    url = f"https://api2.arduino.cc/iot/v2/things/{thing_id}/properties/{property_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_property_timeseries(token, thing_id, property_id, hours=24):
    """Get historical data for trend analysis"""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    url = f"https://api2.arduino.cc/iot/v2/things/{thing_id}/properties/{property_id}/timeseries"
    params = {
        "start": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end": end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "limit": 1000
    }
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def log_voltage(timestamp, voltage):
    """Log voltage reading to CSV"""
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'voltage'])
        writer.writerow([timestamp.isoformat(), voltage])

def get_24h_stats(data):
    """Calculate 24h statistics from historical data"""
    if not data or 'data' not in data or not data['data']:
        return None
    
    values = [float(point['value']) for point in data['data'] if 'value' in point]
    if not values:
        return None
    
    return {
        'count': len(values),
        'min': min(values),
        'max': max(values),
        'avg': sum(values) / len(values),
        'latest': values[-1]
    }

def main():
    # Load configuration
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    
    client_id = config['client_id']
    client_secret = config['client_secret']
    thing_id = config['thing_ids'][0]  # Load Tester_2
    property_id = "6436d48a-7cd2-4ca6-8e0b-1573094f8489"  # TBL3 Voltage property
    
    # Get access token
    token = get_access_token(client_id, client_secret)
    
    # Get current voltage reading
    property_data = get_thing_property(token, thing_id, property_id)
    current_voltage = float(property_data.get('last_value', 0))
    last_updated = property_data.get('updated_at', datetime.now().isoformat())
    
    # Get historical data for trend analysis
    timeseries = get_property_timeseries(token, thing_id, property_id, hours=24)
    
    # Log current reading
    now = datetime.now()
    log_voltage(now, current_voltage)
    
    # Calculate 24h statistics
    stats = get_24h_stats(timeseries)
    
    # Check for alerts
    alerts = []
    if current_voltage < LOW_VOLTAGE_THRESHOLD:
        alerts.append(f"⚠️ LOW VOLTAGE ALERT: {current_voltage:.2f}V (below {LOW_VOLTAGE_THRESHOLD}V threshold)")
    if current_voltage > HIGH_VOLTAGE_THRESHOLD:
        alerts.append(f"⚠️ HIGH VOLTAGE ALERT: {current_voltage:.2f}V (above {HIGH_VOLTAGE_THRESHOLD}V threshold)")
    
    # Generate report
    report_lines = [
        "=" * 50,
        "🔋 Arduino IoT Battery Monitor Report",
        "=" * 50,
        f"📅 Report Time: {now.strftime('%Y-%m-%d %H:%M:%S')} (Asia/Shanghai)",
        f"🔌 Thing: Load Tester_2 ({thing_id})",
        f"📊 Property: TBL3 (Voltage)",
        "",
        "--- Current Reading ---",
        f"Current Voltage: {current_voltage:.3f} V",
        f"Last Updated: {last_updated}",
        "",
    ]
    
    # Add alerts if any
    if alerts:
        report_lines.append("--- ⚠️ ALERTS ---")
        report_lines.extend(alerts)
        report_lines.append("")
    else:
        report_lines.append("--- ✅ Voltage Status: NORMAL ---")
        report_lines.append("")
    
    # Add 24h statistics
    if stats:
        report_lines.extend([
            "--- 24-Hour Statistics ---",
            f"Data Points: {stats['count']}",
            f"Minimum: {stats['min']:.3f} V",
            f"Maximum: {stats['max']:.3f} V",
            f"Average: {stats['avg']:.3f} V",
            "",
        ])
    else:
        report_lines.extend([
            "--- 24-Hour Statistics ---",
            "No historical data available",
            "",
        ])
    
    # Add voltage status assessment
    if 13.0 <= current_voltage <= 14.5:
        status = "Healthy (Normal operating range)"
    elif current_voltage < 13.0:
        status = "Needs Attention (Low battery)"
    else:
        status = "Needs Attention (Possible overcharging)"
    
    report_lines.extend([
        "--- Assessment ---",
        f"Status: {status}",
        "=" * 50,
    ])
    
    report = "\n".join(report_lines)
    
    # Save report
    report_file = os.path.join(DATA_DIR, f"report_{now.strftime('%Y%m%d_%H%M%S')}.txt")
    with open(report_file, 'w') as f:
        f.write(report)
    
    # Output for cron delivery
    print(report)
    
    # Return alert status for external notification
    return {
        'alerts': alerts,
        'current_voltage': current_voltage,
        'stats': stats
    }

if __name__ == "__main__":
    result = main()
    # Exit with non-zero if alerts exist (for cron notification hooks)
    if result['alerts']:
        exit(1)
