# Arduino IoT → GitHub Pipeline

Autonomous sensor data collection from Arduino IoT Cloud to GitHub.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure credentials:**
   ```bash
   cp config/arduino_iot_config.json.template config/arduino_iot_config.json
   # Edit config/arduino_iot_config.json with your credentials
   ```

3. **Check setup:**
   ```bash
   python scripts/run_pipeline.py --check
   ```

4. **Run once (dry run):**
   ```bash
   python scripts/run_pipeline.py --dry-run
   ```

5. **Run and publish:**
   ```bash
   python scripts/run_pipeline.py
   ```

6. **Set up automation:**
   ```bash
   # Run every hour
   python scripts/run_pipeline.py --schedule hourly
   
   # Or every 6 hours
   python scripts/run_pipeline.py --schedule every-6-hours
   
   # Or daily at 9 AM
   python scripts/run_pipeline.py --schedule daily
   ```

## Getting Arduino Cloud Credentials

1. Go to [Arduino Cloud](https://cloud.arduino.cc/)
2. Navigate to **API Keys** section
3. Click **"CREATE API KEY"**
4. Save the Client ID and Client Secret
5. Get your Thing ID from the Thing's **Metadata** tab

## File Structure

```
├── config/
│   ├── arduino_iot_config.json          # Your credentials (gitignored)
│   └── arduino_iot_config.json.template # Template
├── scripts/
│   ├── run_pipeline.py                  # Main entry point
│   ├── arduino_collector.py             # IoT Cloud API
│   ├── report_generator.py              # Markdown reports
│   └── git_publisher.py                 # Git operations
├── reports/                             # Generated reports
│   └── YYYY-MM-DD/
│       └── sensor-report-HHMM.md
├── requirements.txt
└── README.md
```

## Troubleshooting

### "Config file not found"
Make sure you've created `config/arduino_iot_config.json` from the template.

### "Failed to get access token"
Check your Client ID and Client Secret. They must match exactly what's in Arduino Cloud.

### "Not in a git repository"
Run `git init` in the pipeline directory or clone from an existing GitHub repo.

### "No remote configured"
Set up the GitHub remote: `git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git`

## Automation

The pipeline uses cron for scheduling. To view your scheduled jobs:
```bash
crontab -l
```

To remove the scheduled job:
```bash
crontab -e
# Delete the line containing "run_pipeline.py"
```
