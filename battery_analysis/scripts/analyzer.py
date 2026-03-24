#!/usr/bin/env python3
"""
Battery Voltage Analyzer - Arduino IoT Cloud API
Fetches voltage data and generates intelligent analysis reports.
"""

import os
import sys
import json
import csv
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# Configuration
CONFIG_PATH = Path("/root/.openclaw/workspace/battery_analysis/config.json")
DATA_PATH = Path("/root/.openclaw/workspace/battery_analysis/data")
REPORTS_PATH = Path("/root/.openclaw/workspace/battery_analysis/reports")
CREDENTIALS_PATH = Path("/root/.openclaw/workspace/.arduino_credentials")

# Voltage thresholds for 12V lead-acid battery
VOLTAGE_THRESHOLDS = {
    "critical_low": 11.8,      # Deep discharge danger
    "low": 12.2,               # Needs charging
    "nominal_min": 12.6,       # Normal minimum (resting)
    "nominal_max": 13.8,       # Normal maximum (charging)
    "high": 14.8,              # Overcharge warning
    "critical_high": 15.5      # Dangerous overcharge
}

class ArduinoIoTClient:
    """Simple Arduino IoT Cloud API client using username/password auth."""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.base_url = "https://api2.arduino.cc/iot/v1"
        self.token = None
        self.token_expires = None
        
    def _get_token(self) -> str:
        """Get OAuth2 access token."""
        if self.token and self.token_expires and datetime.now() < self.token_expires:
            return self.token
            
        url = "https://api2.arduino.cc/iot/v1/clients/token"
        payload = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
            "client_id": "4SMK7nCETqjLkg",
            "client_secret": ""
        }
        
        response = requests.post(url, data=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        self.token = data["access_token"]
        expires_in = data.get("expires_in", 300)
        self.token_expires = datetime.now() + timedelta(seconds=expires_in - 60)
        
        return self.token
    
    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make authenticated API request."""
        token = self._get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{endpoint}"
        response = requests.request(method, url, headers=headers, timeout=30, **kwargs)
        response.raise_for_status()
        
        if response.status_code == 204:
            return {}
        return response.json()
    
    def get_things(self) -> List[dict]:
        """Get all Things (devices)."""
        return self._request("GET", "things")
    
    def get_properties(self, thing_id: str) -> List[dict]:
        """Get all properties (variables) for a Thing."""
        return self._request("GET", f"things/{thing_id}/properties")
    
    def get_property_value(self, thing_id: str, property_id: str) -> dict:
        """Get current value of a property."""
        return self._request("GET", f"things/{thing_id}/properties/{property_id}/timeseries")
    
    def get_timeseries(self, thing_id: str, property_id: str, 
                       start_time: datetime, end_time: datetime) -> List[dict]:
        """Get historical timeseries data."""
        # Arduino API expects ISO format with Z
        start_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        endpoint = f"things/{thing_id}/properties/{property_id}/timeseries"
        params = {"from": start_str, "to": end_str, "interval": 60}
        
        return self._request("GET", endpoint, params=params)


class BatteryAnalyzer:
    """Analyze battery voltage data and generate reports."""
    
    def __init__(self, client: ArduinoIoTClient, thing_id: str, property_name: str = "voltage"):
        self.client = client
        self.thing_id = thing_id
        self.property_name = property_name
        self.property_id = None
        
    def find_voltage_property(self) -> Optional[str]:
        """Find the voltage property ID."""
        properties = self.client.get_properties(self.thing_id)
        
        for prop in properties:
            name = prop.get("name", "").lower()
            var_name = prop.get("variable_name", "").lower()
            
            if any(word in name or word in var_name for word in 
                   ["voltage", "volt", "battery", "batt"]):
                self.property_id = prop["id"]
                return self.property_id
        
        # Fallback: take first FLOAT property
        for prop in properties:
            if prop.get("type") == "FLOAT":
                self.property_id = prop["id"]
                return self.property_id
                
        return None
    
    def fetch_data(self, hours_back: int = 24) -> List[dict]:
        """Fetch voltage data for specified hours back."""
        if not self.property_id:
            if not self.find_voltage_property():
                raise ValueError("Could not find voltage property")
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours_back)
        
        return self.client.get_timeseries(self.thing_id, self.property_id, 
                                          start_time, end_time)
    
    def analyze(self, data: List[dict]) -> dict:
        """Analyze voltage data and return statistics."""
        if not data:
            return {"error": "No data available"}
        
        values = [float(point.get("value", 0)) for point in data if point.get("value")]
        
        if not values:
            return {"error": "No valid voltage readings"}
        
        current = values[-1]
        min_v = min(values)
        max_v = max(values)
        avg_v = sum(values) / len(values)
        
        # Calculate trend (last 6 hours vs previous)
        trend = "stable"
        if len(values) >= 12:
            recent = sum(values[-6:]) / 6
            previous = sum(values[-12:-6]) / 6
            diff = recent - previous
            
            if diff > 0.1:
                trend = "rising"
            elif diff < -0.1:
                trend = "falling"
        
        # Determine health status
        status = self._get_status(current)
        health_score = self._calculate_health_score(current, min_v, max_v)
        
        # Calculate time in each voltage range
        range_times = self._calculate_range_times(values)
        
        return {
            "current": round(current, 3),
            "min": round(min_v, 3),
            "max": round(max_v, 3),
            "average": round(avg_v, 3),
            "trend": trend,
            "status": status,
            "health_score": health_score,
            "data_points": len(values),
            "range_distribution": range_times,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_status(self, voltage: float) -> str:
        """Get battery status based on voltage."""
        t = VOLTAGE_THRESHOLDS
        
        if voltage <= t["critical_low"]:
            return "🔴 CRITICAL LOW - Deep discharge danger!"
        elif voltage <= t["low"]:
            return "🟠 LOW - Needs charging soon"
        elif voltage <= t["nominal_min"]:
            return "🟡 BELOW NOMINAL - Resting, not charging"
        elif voltage <= t["nominal_max"]:
            return "🟢 HEALTHY - Normal operating range"
        elif voltage <= t["high"]:
            return "🔵 CHARGING - Normal charge voltage"
        elif voltage <= t["critical_high"]:
            return "🟠 HIGH - Overcharge warning"
        else:
            return "🔴 CRITICAL HIGH - Dangerous overcharge!"
    
    def _calculate_health_score(self, current: float, min_v: float, max_v: float) -> int:
        """Calculate battery health score (0-100)."""
        score = 100
        
        # Penalize deep discharge
        if min_v < 11.5:
            score -= 30
        elif min_v < 12.0:
            score -= 15
        
        # Penalize overcharge
        if max_v > 15.0:
            score -= 25
        elif max_v > 14.8:
            score -= 10
        
        # Penalize large voltage swings
        swing = max_v - min_v
        if swing > 2.0:
            score -= 15
        elif swing > 1.5:
            score -= 5
        
        # Current voltage health
        if 12.6 <= current <= 14.8:
            pass  # Good range
        elif 12.0 <= current < 12.6:
            score -= 5
        elif current < 12.0:
            score -= 15
        
        return max(0, min(100, score))
    
    def _calculate_range_times(self, values: List[float]) -> dict:
        """Calculate percentage of time in each voltage range."""
        if not values:
            return {}
        
        t = VOLTAGE_THRESHOLDS
        ranges = {
            "critical_low": 0,
            "low": 0,
            "nominal": 0,
            "charging": 0,
            "high": 0
        }
        
        for v in values:
            if v <= t["critical_low"]:
                ranges["critical_low"] += 1
            elif v <= t["low"]:
                ranges["low"] += 1
            elif v <= t["nominal_max"]:
                ranges["nominal"] += 1
            elif v <= t["high"]:
                ranges["charging"] += 1
            else:
                ranges["high"] += 1
        
        total = len(values)
        return {k: round(v/total*100, 1) for k, v in ranges.items()}


def load_credentials() -> Tuple[str, str]:
    """Load Arduino credentials from file."""
    with open(CREDENTIALS_PATH, 'r') as f:
        for line in f:
            if line.startswith("ARDUINO_IOT_USERNAME="):
                username = line.split("=", 1)[1].strip()
            elif line.startswith("ARDUINO_IOT_PASSWORD="):
                password = line.split("=", 1)[1].strip()
    
    return username, password


def save_to_csv(analysis: dict, data: List[dict]):
    """Save analysis and raw data to CSV."""
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    
    # Daily summary CSV
    summary_file = DATA_PATH / "daily_summary.csv"
    summary_exists = summary_file.exists()
    
    with open(summary_file, 'a', newline='') as f:
        writer = csv.writer(f)
        if not summary_exists:
            writer.writerow([
                "timestamp", "current_v", "min_v", "max_v", "avg_v", 
                "trend", "status", "health_score", "data_points"
            ])
        
        writer.writerow([
            analysis.get("timestamp", ""),
            analysis.get("current", ""),
            analysis.get("min", ""),
            analysis.get("max", ""),
            analysis.get("average", ""),
            analysis.get("trend", ""),
            analysis.get("status", "").replace("🔴", "CRIT").replace("🟠", "LOW")
                .replace("🟡", "BELOW").replace("🟢", "HEALTHY").replace("🔵", "CHARGING"),
            analysis.get("health_score", ""),
            analysis.get("data_points", "")
        ])
    
    # Raw data CSV with timestamp
    today = datetime.now().strftime("%Y%m%d")
    raw_file = DATA_PATH / f"voltage_raw_{today}.csv"
    
    with open(raw_file, 'a', newline='') as f:
        writer = csv.writer(f)
        for point in data:
            writer.writerow([
                point.get("time", ""),
                point.get("value", "")
            ])


def generate_report(analysis: dict, period: str = "24h") -> str:
    """Generate markdown report."""
    REPORTS_PATH.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_file = REPORTS_PATH / f"battery_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    
    range_dist = analysis.get("range_distribution", {})
    
    report = f"""# 🔋 Battery Voltage Report - {period.upper()}

**Generated:** {timestamp}  
**Period:** Last {period}

---

## 📊 Current Status

| Metric | Value |
|--------|-------|
| **Current Voltage** | **{analysis.get('current', 'N/A')} V** |
| **24h Minimum** | {analysis.get('min', 'N/A')} V |
| **24h Maximum** | {analysis.get('max', 'N/A')} V |
| **Average** | {analysis.get('average', 'N/A')} V |
| **Trend** | {analysis.get('trend', 'N/A').upper()} |
| **Health Score** | {analysis.get('health_score', 'N/A')}/100 |

### Status: {analysis.get('status', 'Unknown')}

---

## 📈 Voltage Range Distribution (24h)

| Range | Percentage |
|-------|------------|
| 🔴 Critical Low (≤11.8V) | {range_dist.get('critical_low', 0)}% |
| 🟠 Low (11.8-12.2V) | {range_dist.get('low', 0)}% |
| 🟢 Nominal (12.2-13.8V) | {range_dist.get('nominal', 0)}% |
| 🔵 Charging (13.8-14.8V) | {range_dist.get('charging', 0)}% |
| 🟠 High (>14.8V) | {range_dist.get('high', 0)}% |

---

## 🎯 Recommendations

"""
    
    # Add recommendations based on analysis
    health = analysis.get('health_score', 50)
    trend = analysis.get('trend', 'stable')
    status = analysis.get('status', '')
    
    if health < 50:
        report += "- ⚠️ **Battery health is poor** - Consider inspecting the battery and charging system\n"
    elif health < 75:
        report += "- 📋 **Battery health is fair** - Monitor closely for any deterioration\n"
    else:
        report += "- ✅ **Battery is in good health** - Continue normal monitoring\n"
    
    if "CRITICAL" in status:
        report += "- 🚨 **URGENT ACTION REQUIRED** - Check battery and charging system immediately!\n"
    elif "LOW" in status and "Needs" in status:
        report += "- 🔌 **Charge the battery soon** to prevent deep discharge damage\n"
    
    if trend == "falling":
        report += "- 📉 **Voltage is trending down** - If not charging, battery may need attention\n"
    elif trend == "rising":
        report += "- 📈 **Voltage is trending up** - Battery is likely charging normally\n"
    
    report += f"""
---

## 📋 Data Summary

- **Data Points Analyzed:** {analysis.get('data_points', 'N/A')}
- **Voltage Swing:** {round(analysis.get('max', 0) - analysis.get('min', 0), 3)} V

---

*Report generated by Orthia Battery Monitor*
"""
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    return str(report_file)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Battery Voltage Analyzer')
    parser.add_argument('--thing-id', default='df883ac4-b65c-40b2-9a96-b3b01adffe1d',
                        help='Arduino Thing ID')
    parser.add_argument('--hours', type=int, default=24,
                        help='Hours of data to analyze')
    parser.add_argument('--format', choices=['text', 'json', 'table'], default='table',
                        help='Output format')
    
    args = parser.parse_args()
    
    try:
        # Load credentials
        username, password = load_credentials()
        
        # Initialize client
        client = ArduinoIoTClient(username, password)
        
        # Initialize analyzer
        analyzer = BatteryAnalyzer(client, args.thing_id)
        
        # Fetch and analyze data
        print(f"🔍 Fetching {args.hours}h of voltage data...")
        data = analyzer.fetch_data(args.hours)
        print(f"📊 Analyzing {len(data)} data points...")
        
        analysis = analyzer.analyze(data)
        
        if "error" in analysis:
            print(f"❌ Error: {analysis['error']}")
            return 1
        
        # Save data
        save_to_csv(analysis, data)
        
        # Generate report
        report_path = generate_report(analysis, f"{args.hours}h")
        
        # Output results
        if args.format == 'json':
            print(json.dumps(analysis, indent=2))
        elif args.format == 'table':
            print(f"""
╔══════════════════════════════════════════════════════╗
║           BATTERY VOLTAGE REPORT - {args.hours}H              ║
╠══════════════════════════════════════════════════════╣
║  Current:      {analysis['current']:>6.3f} V                          ║
║  24h Min:      {analysis['min']:>6.3f} V                          ║
║  24h Max:      {analysis['max']:>6.3f} V                          ║
║  Average:      {analysis['average']:>6.3f} V                          ║
║  Trend:        {analysis['trend'].upper():<15}                    ║
║  Health:       {analysis['health_score']}/100{' ' * (26 if analysis['health_score'] < 10 else 25)}║
╠══════════════════════════════════════════════════════╣
║  Status: {analysis['status'][:45]:<45} ║
╚══════════════════════════════════════════════════════╝
            """)
        else:
            print(f"Current: {analysis['current']} V | Min: {analysis['min']} V | Max: {analysis['max']} V")
            print(f"Trend: {analysis['trend']} | Health: {analysis['health_score']}/100")
            print(f"Status: {analysis['status']}")
        
        print(f"\n📄 Report saved: {report_path}")
        print(f"📁 Data logged: {DATA_PATH}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
