#!/usr/bin/env python3
"""
Improved Battery Monitor - Arduino IoT Cloud with proper API authentication.
Requires: Arduino IoT Cloud API Key (Client ID + Client Secret)
"""

import os
import sys
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Tuple

try:
    from arduino_iot_cloud import ArduinoIoTCloudClient
except ImportError:
    print("Installing arduino-iot-cloud package...")
    os.system("pip install arduino-iot-cloud -q")
    from arduino_iot_cloud import ArduinoIoTCloudClient

# Paths
DATA_PATH = Path("/root/.openclaw/workspace/battery_analysis/data")
REPORTS_PATH = Path("/root/.openclaw/workspace/battery_analysis/reports")
CONFIG_PATH = Path("/root/.openclaw/workspace/battery_analysis/config.json")
CREDENTIALS_PATH = Path("/root/.openclaw/workspace/.arduino_credentials")

# Voltage thresholds for 12V lead-acid battery
THRESHOLDS = {
    "critical_low": 11.8, "low": 12.2, "nominal_min": 12.6,
    "nominal_max": 13.8, "high": 14.8, "critical_high": 15.5
}

class BatteryMonitor:
    def __init__(self, client_id: str, client_secret: str, thing_id: str):
        self.client = ArduinoIoTCloudClient(client_id=client_id, client_secret=client_secret)
        self.thing_id = thing_id
        
    def get_voltage_property(self) -> Optional[str]:
        """Find voltage property ID."""
        try:
            things = self.client.things.list()
            for thing in things:
                if str(thing.id) == self.thing_id:
                    for prop in thing.properties:
                        name = str(prop.name).lower()
                        if any(w in name for w in ["voltage", "volt", "battery", "batt"]):
                            return prop.id
            # Fallback: first numeric property
            for thing in things:
                if str(thing.id) == self.thing_id:
                    for prop in thing.properties:
                        if prop.type in ["FLOAT", "INT"]:\n                            return prop.id
        except Exception as e:
            print(f"Error finding property: {e}")
        return None
    
    def fetch_timeseries(self, property_id: str, hours: int = 24) -> List[dict]:
        """Fetch historical data."""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        try:
            data = self.client.properties.timeseries(
                thing_id=self.thing_id,
                property_id=property_id,
                start=start_time.isoformat() + "Z",
                end=end_time.isoformat() + "Z",
                interval=300  # 5-minute intervals
            )
            return data
        except Exception as e:
            print(f"Error fetching timeseries: {e}")
            return []
    
    def analyze(self, data: List[dict]) -> dict:
        """Analyze voltage data."""
        if not data:
            return {"error": "No data available"}
        
        values = [float(d.get("value", 0)) for d in data if d.get("value")]
        if not values:
            return {"error": "No valid readings"}
        
        current = values[-1]
        min_v, max_v = min(values), max(values)
        avg_v = sum(values) / len(values)
        
        # Trend analysis
        trend = "stable"
        if len(values) >= 12:
            recent = sum(values[-6:]) / 6
            previous = sum(values[-12:-6]) / 6
            diff = recent - previous
            trend = "rising" if diff > 0.1 else "falling" if diff < -0.1 else "stable"
        
        # Health score
        health = 100
        if min_v < 11.5: health -= 30
        elif min_v < 12.0: health -= 15
        if max_v > 15.0: health -= 25
        elif max_v > 14.8: health -= 10
        health = max(0, min(100, health))
        
        # Status
        status = self._status(current)
        
        return {
            "current": round(current, 3), "min": round(min_v, 3),
            "max": round(max_v, 3), "average": round(avg_v, 3),
            "trend": trend, "status": status, "health_score": health,
            "data_points": len(values), "timestamp": datetime.now().isoformat()
        }
    
    def _status(self, v: float) -> str:
        t = THRESHOLDS
        if v <= t["critical_low"]: return "🔴 CRITICAL LOW"
        elif v <= t["low"]: return "🟠 LOW - Needs charging"
        elif v <= t["nominal_min"]: return "🟡 RESTING"
        elif v <= t["nominal_max"]: return "🟢 HEALTHY"
        elif v <= t["high"]: return "🔵 CHARGING"
        elif v <= t["critical_high"]: return "🟠 HIGH"
        return "🔴 CRITICAL HIGH"


def load_config() -> dict:
    """Load or create config."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    
    # Create template
    config = {
        "client_id": "YOUR_CLIENT_ID_HERE",
        "client_secret": "YOUR_CLIENT_SECRET_HERE",
        "thing_id": "df883ac4-b65c-40b2-9a96-b3b01adffe1d",
        "property_name": "voltage"
    }
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"⚠️  Config template created at {CONFIG_PATH}")
    print("Please add your Arduino IoT Cloud API credentials.")
    return config


def save_data(analysis: dict):
    """Save to CSV."""
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    csv_file = DATA_PATH / "battery_history.csv"
    
    exists = csv_file.exists()
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["timestamp", "current", "min", "max", "avg", "trend", "health"])
        writer.writerow([
            analysis.get("timestamp"), analysis.get("current"),
            analysis.get("min"), analysis.get("max"), analysis.get("average"),
            analysis.get("trend"), analysis.get("health_score")
        ])


def generate_report(analysis: dict) -> str:
    """Generate markdown report."""
    REPORTS_PATH.mkdir(parents=True, exist_ok=True)
    
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    report_file = REPORTS_PATH / f"report_{ts}.md"
    
    report = f"""# 🔋 Battery Report

**Generated:** {analysis.get('timestamp', 'N/A')}

## Current Status

| Metric | Value |
|--------|-------|
| Voltage | **{analysis.get('current', 'N/A')} V** |
| 24h Min | {analysis.get('min', 'N/A')} V |
| 24h Max | {analysis.get('max', 'N/A')} V |
| Average | {analysis.get('average', 'N/A')} V |
| Trend | {analysis.get('trend', 'N/A').upper()} |
| Health | {analysis.get('health_score', 'N/A')}/100 |

**Status:** {analysis.get('status', 'N/A')}

---
*Orthia Battery Monitor*
"""
    
    with open(report_file, 'w') as f:
        f.write(report)
    return str(report_file)


def main():
    config = load_config()
    
    if "YOUR_" in config.get("client_id", ""):
        print("""
╔════════════════════════════════════════════════════════════╗
║  ⚠️  ARDUINO IOT CLOUD API CREDENTIALS REQUIRED            ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  To use this monitor, you need to create an API key:       ║
║                                                            ║
║  1. Go to: https://cloud.arduino.cc/                      ║
║  2. Click your profile → API Keys → Create                 ║
║  3. Copy the Client ID and Client Secret                   ║
║  4. Edit: /root/.openclaw/workspace/battery_analysis/     ║
║           config.json                                      ║
║                                                            ║
║  Note: The Client Secret is shown ONLY ONCE as a PDF.      ║
║        Save it immediately!                                ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
        """)
        return 1
    
    try:
        print("🔌 Connecting to Arduino IoT Cloud...")
        monitor = BatteryMonitor(
            config["client_id"],
            config["client_secret"],
            config["thing_id"]
        )
        
        print("🔍 Finding voltage property...")
        prop_id = monitor.get_voltage_property()
        if not prop_id:
            print("❌ Could not find voltage property")
            return 1
        
        print(f"📊 Fetching 24h data...")
        data = monitor.fetch_timeseries(prop_id, hours=24)
        
        print(f"🧮 Analyzing {len(data)} points...")
        analysis = monitor.analyze(data)
        
        if "error" in analysis:
            print(f"❌ {analysis['error']}")
            return 1
        
        # Save and report
        save_data(analysis)
        report_path = generate_report(analysis)
        
        # Print summary
        print(f"""
╔══════════════════════════════════════════════════════╗
║              BATTERY VOLTAGE REPORT                   ║
╠══════════════════════════════════════════════════════╣
║  Current:   {analysis['current']:>6.3f} V                          ║
║  24h Min:   {analysis['min']:>6.3f} V                          ║
║  24h Max:   {analysis['max']:>6.3f} V                          ║
║  Trend:     {analysis['trend'].upper():<15}                    ║
║  Health:    {analysis['health_score']}/100                           ║
╠══════════════════════════════════════════════════════╣
║  {analysis['status'][:48]:<48}  ║
╚══════════════════════════════════════════════════════╝
        """)
        print(f"📄 Report: {report_path}")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
