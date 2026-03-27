#!/usr/bin/env python3
"""
Arduino IoT Cloud Battery Monitor - API Version
Fetches voltage data using Arduino IoT Cloud REST API
"""

import json
import os
import sys
import csv
import base64
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
CONFIG_FILE = "/root/.openclaw/workspace/arduino-iot-pipeline/config/arduino_iot_config.json"
CSV_FILE = "/root/.openclaw/workspace/battery_data/voltage_log.csv"
REPORT_FILE = "/root/.openclaw/workspace/battery_data/latest_report.txt"
ALERT_STATE_FILE = "/root/.openclaw/workspace/battery_data/alert_state.json"

# Arduino IoT Cloud API
IOT_API_BASE = "https://api2.arduino.cc/iot/v1"
AUTH_URL = "https://api2.arduino.cc/iot/v1/clients/token"

# Alert thresholds (updated per user request)
ALERT_LOW = 13.45
ALERT_HIGH = 14.65

# Alert rate limiting - minimum minutes between repeat alerts
ALERT_COOLDOWN_MINUTES = 30

# Telegram Bot Token (stored in environment or config)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def load_config():
    """Load Arduino IoT Cloud credentials"""
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def load_alert_state():
    """Load alert state to track when last alerts were sent"""
    if os.path.exists(ALERT_STATE_FILE):
        try:
            with open(ALERT_STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"low_alert_time": None, "high_alert_time": None}

def save_alert_state(state):
    """Save alert state to file"""
    with open(ALERT_STATE_FILE, 'w') as f:
        json.dump(state, f)

def should_send_alert(alert_type, current_time):
    """
    Check if we should send an alert based on rate limiting.
    Returns True if:
    - No previous alert of this type exists, OR
    - 30+ minutes have passed since the last alert of this type
    """
    state = load_alert_state()
    last_alert_key = f"{alert_type.lower()}_alert_time"
    last_alert_time = state.get(last_alert_key)
    
    if last_alert_time is None:
        return True
    
    try:
        last_time = datetime.fromisoformat(last_alert_time)
        minutes_since = (current_time - last_time).total_seconds() / 60
        return minutes_since >= ALERT_COOLDOWN_MINUTES
    except:
        return True

def record_alert_sent(alert_type, current_time):
    """Record that an alert was sent at the current time"""
    state = load_alert_state()
    state[f"{alert_type.lower()}_alert_time"] = current_time.isoformat()
    save_alert_state(state)

def clear_alert_state(alert_type):
    """Clear alert state when voltage returns to normal"""
    state = load_alert_state()
    state[f"{alert_type.lower()}_alert_time"] = None
    save_alert_state(state)

def get_access_token(client_id, client_secret):
    """Get OAuth2 access token from Arduino IoT Cloud"""
    auth_string = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    
    headers = {
        "Authorization": f"Basic {auth_string}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "client_credentials"
    }
    
    try:
        response = requests.post(AUTH_URL, headers=headers, data=data, timeout=30)
        response.raise_for_status()
        token_data = response.json()
        return token_data.get("access_token")
    except Exception as e:
        print(f"Error getting access token: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return None

def get_thing_properties(token, thing_id):
    """Get all properties for a thing"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"{IOT_API_BASE}/things/{thing_id}/properties"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting properties: {e}")
        return None

def get_property_data(token, thing_id, property_id, start_time=None, end_time=None, interval=3600):
    """Get historical data for a property"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"{IOT_API_BASE}/things/{thing_id}/properties/{property_id}/timeseries"
    
    params = {}
    if start_time:
        params['start'] = start_time.isoformat() + 'Z'
    if end_time:
        params['end'] = end_time.isoformat() + 'Z'
    if interval:
        params['interval'] = interval
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting timeseries data: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status: {e.response.status_code}")
            print(f"Response: {e.response.text[:500]}")
        return None

def get_property_value(token, thing_id, property_id):
    """Get current value of a property"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"{IOT_API_BASE}/things/{thing_id}/properties/{property_id}"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting property value: {e}")
        return None

def log_voltage(voltage, min_val=None, max_val=None, avg_val=None):
    """Log voltage to CSV file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    file_exists = os.path.exists(CSV_FILE)
    
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'current_voltage', 'min_24h', 'max_24h', 'avg_24h'])
        writer.writerow([timestamp, f"{voltage:.3f}"] + 
                       [f"{v:.3f}" if v else "" for v in [min_val, max_val, avg_val]])
    
    return timestamp

def send_telegram_alert(message):
    """Send alert via Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[TELEGRAM ALERT - NOT SENT]: {message}")
        print("(Telegram credentials not configured)")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, data=data, timeout=30)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending Telegram alert: {e}")
        return False

def analyze_24h_stats(values):
    """Calculate 24-hour statistics"""
    if not values:
        return None, None, None
    
    numeric_values = [v['value'] for v in values if isinstance(v.get('value'), (int, float))]
    if not numeric_values:
        return None, None, None
    
    return min(numeric_values), max(numeric_values), sum(numeric_values) / len(numeric_values)

def main():
    print("=" * 60)
    print("  Arduino IoT Battery Monitor - Hourly Check")
    print("=" * 60)
    
    current_time = datetime.now()
    print(f"\nTimestamp: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load configuration
    try:
        config = load_config()
        client_id = config.get('client_id')
        client_secret = config.get('client_secret')
        thing_id = config.get('thing_ids', ['37cd8c67-7ebf-401f-a88e-321c9a285c4a'])[0]
    except Exception as e:
        print(f"ERROR: Failed to load configuration: {e}")
        return 1
    
    print(f"\nThing ID: {thing_id}")
    print(f"Alert Thresholds: LOW < {ALERT_LOW}V | HIGH > {ALERT_HIGH}V")
    print(f"Alert Cooldown: {ALERT_COOLDOWN_MINUTES} minutes between repeat alerts")
    print("\nAuthenticating with Arduino IoT Cloud...")
    
    # Get access token
    token = get_access_token(client_id, client_secret)
    if not token:
        print("ERROR: Failed to obtain access token")
        return 1
    
    print("✓ Authentication successful")
    
    # Get thing properties
    print("\nFetching thing properties...")
    properties = get_thing_properties(token, thing_id)
    if not properties:
        print("ERROR: Failed to get properties")
        return 1
    
    # Find voltage property (TBL3)
    voltage_property = None
    for prop in properties:
        if prop.get('name') == 'TBL3' or prop.get('variable_name') == 'TBL3':
            voltage_property = prop
            break
    
    if not voltage_property:
        print("WARNING: TBL3 property not found, checking all properties...")
        for prop in properties:
            print(f"  - {prop.get('name')} ({prop.get('type')})")
            if prop.get('type') == 'FLOAT' or 'voltage' in str(prop.get('name', '')).lower():
                voltage_property = prop
                break
    
    if not voltage_property:
        print("ERROR: Could not find voltage property")
        return 1
    
    property_id = voltage_property.get('id')
    print(f"✓ Found voltage property: {voltage_property.get('name')} (ID: {property_id})")
    
    # Get current value
    print("\nFetching current voltage...")
    current_data = get_property_value(token, thing_id, property_id)
    if not current_data:
        print("ERROR: Failed to get current voltage")
        return 1
    
    current_voltage = current_data.get('last_value')
    if current_voltage is None:
        print("ERROR: No voltage value available")
        return 1
    
    try:
        current_voltage = float(current_voltage)
    except:
        print(f"ERROR: Invalid voltage value: {current_voltage}")
        return 1
    
    print(f"✓ Current voltage: {current_voltage:.3f} V")
    
    # Get 24-hour historical data
    print("\nFetching 24-hour historical data...")
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
    
    timeseries_data = get_property_data(token, thing_id, property_id, start_time, end_time)
    
    min_24h, max_24h, avg_24h = None, None, None
    if timeseries_data and 'data' in timeseries_data:
        values = timeseries_data['data']
        min_24h, max_24h, avg_24h = analyze_24h_stats(values)
        print(f"✓ Retrieved {len(values)} data points")
    else:
        print("⚠ No historical data available")
    
    # Log to CSV
    timestamp = log_voltage(current_voltage, min_24h, max_24h, avg_24h)
    print(f"✓ Logged to {CSV_FILE}")
    
    # Check for alerts with rate limiting
    alerts = []
    alert_state = load_alert_state()
    
    if current_voltage < ALERT_LOW:
        if should_send_alert("low", current_time):
            alert_msg = f"🚨 BATTERY ALERT: Voltage LOW\n\nCurrent: {current_voltage:.3f} V\nThreshold: < {ALERT_LOW:.2f} V\n\nTime: {timestamp}\n\n_Next alert in {ALERT_COOLDOWN_MINUTES} min if still low_"
            alerts.append(("LOW", alert_msg))
            record_alert_sent("low", current_time)
        else:
            # Calculate time until next alert
            last_time = datetime.fromisoformat(alert_state.get("low_alert_time"))
            minutes_since = (current_time - last_time).total_seconds() / 60
            minutes_remaining = ALERT_COOLDOWN_MINUTES - minutes_since
            print(f"\n⚠️  LOW voltage detected ({current_voltage:.3f}V) - Alert suppressed ({minutes_remaining:.0f} min until next alert)")
    else:
        # Clear low alert state if voltage recovered
        if alert_state.get("low_alert_time"):
            clear_alert_state("low")
            print("\n✓ Voltage recovered from LOW - Alert state reset")
    
    if current_voltage > ALERT_HIGH:
        if should_send_alert("high", current_time):
            alert_msg = f"🚨 BATTERY ALERT: Voltage HIGH\n\nCurrent: {current_voltage:.3f} V\nThreshold: > {ALERT_HIGH:.2f} V\n\nTime: {timestamp}\n\n_Next alert in {ALERT_COOLDOWN_MINUTES} min if still high_"
            alerts.append(("HIGH", alert_msg))
            record_alert_sent("high", current_time)
        else:
            # Calculate time until next alert
            last_time = datetime.fromisoformat(alert_state.get("high_alert_time"))
            minutes_since = (current_time - last_time).total_seconds() / 60
            minutes_remaining = ALERT_COOLDOWN_MINUTES - minutes_since
            print(f"\n⚠️  HIGH voltage detected ({current_voltage:.3f}V) - Alert suppressed ({minutes_remaining:.0f} min until next alert)")
    else:
        # Clear high alert state if voltage recovered
        if alert_state.get("high_alert_time"):
            clear_alert_state("high")
            print("\n✓ Voltage recovered from HIGH - Alert state reset")
    
    # Send alerts
    if alerts:
        print(f"\n🚨 ALERTS SENT ({len(alerts)}):")
        for alert_type, alert_msg in alerts:
            print(f"   - {alert_type}: {current_voltage:.3f}V")
            send_telegram_alert(alert_msg)
    else:
        print(f"\n✓ Voltage within normal range ({ALERT_LOW}V - {ALERT_HIGH}V)")
    
    # Generate report
    report = []
    report.append("=" * 50)
    report.append("  BATTERY VOLTAGE REPORT")
    report.append("=" * 50)
    report.append(f"")
    report.append(f"Report Time:   {timestamp}")
    report.append(f"Thing:         Load Tester_2")
    report.append(f"")
    report.append(f"CURRENT READING")
    report.append(f"  Voltage:     {current_voltage:.3f} V")
    report.append(f"")
    report.append(f"24-HOUR STATISTICS")
    if min_24h is not None:
        report.append(f"  Minimum:     {min_24h:.3f} V")
        report.append(f"  Maximum:     {max_24h:.3f} V")
        report.append(f"  Average:     {avg_24h:.3f} V")
    else:
        report.append(f"  (No historical data available)")
    report.append(f"")
    report.append(f"ALERT STATUS")
    if current_voltage < ALERT_LOW:
        report.append(f"  ⚠️  LOW VOLTAGE ALERT")
        report.append(f"      Current: {current_voltage:.3f} V < {ALERT_LOW:.2f} V")
    elif current_voltage > ALERT_HIGH:
        report.append(f"  ⚠️  HIGH VOLTAGE ALERT")
        report.append(f"      Current: {current_voltage:.3f} V > {ALERT_HIGH:.2f} V")
    else:
        report.append(f"  ✓ Normal - within safe range")
    report.append(f"")
    report.append(f"THRESHOLDS")
    report.append(f"  Low Alert:   < {ALERT_LOW:.2f} V")
    report.append(f"  High Alert:  > {ALERT_HIGH:.2f} V")
    report.append(f"  Alert Rate:  Max 1 per {ALERT_COOLDOWN_MINUTES} min while out of bounds")
    report.append("=" * 50)
    
    report_text = "\n".join(report)
    
    # Save report
    with open(REPORT_FILE, 'w') as f:
        f.write(report_text)
    
    # Print report
    print("\n" + report_text)
    
    print(f"\n✓ Report saved to {REPORT_FILE}")
    print("\n" + "=" * 60)
    print("  Battery Monitor Check Complete")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
