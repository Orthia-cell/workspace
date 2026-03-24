#!/bin/bash
# Improved Battery Monitor - Run by Cron
# This script provides robust battery voltage monitoring with API-based collection

set -e

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/battery_analysis/data/cron.log"

cd "$WORKSPACE"

# Ensure directories exist
mkdir -p "$WORKSPACE/battery_analysis/data"
mkdir -p "$WORKSPACE/battery_analysis/reports"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting battery monitoring check..."

# Check if API credentials are configured
if [ -f "$WORKSPACE/battery_analysis/config.json" ]; then
    if grep -q "YOUR_CLIENT_ID" "$WORKSPACE/battery_analysis/config.json"; then
        log "⚠️  API credentials not configured. Please set up config.json"
        echo "BATTERY_MONITOR: API credentials needed. Edit battery_analysis/config.json"
        exit 1
    fi
    
    # Run the API-based monitor
    log "Running API-based monitor..."
    if python3 "$WORKSPACE/battery_analysis/scripts/battery_monitor.py"; then
        log "✅ Monitor completed successfully"
    else
        log "❌ Monitor failed"
        exit 1
    fi
else
    log "⚠️  Config file not found. Creating template..."
    cp "$WORKSPACE/battery_analysis/config.json.template" "$WORKSPACE/battery_analysis/config.json"
    echo "BATTERY_MONITOR: Config template created. Please add API credentials."
    exit 1
fi
