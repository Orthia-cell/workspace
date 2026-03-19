# Arduino IoT → GitHub Report Pipeline

**Project Status:** ✅ BUILT, ⏳ AWAITING CREDENTIALS  
**Created:** 2026-03-14 (4:20 AM Asia/Shanghai)  
**Last Updated:** 2026-03-14 (5:50 AM Asia/Shanghai)  
**Purpose:** Autonomous sensor data collection from Arduino IoT Cloud → Markdown reports → GitHub repository

---

## Quick Status

| Component | Status |
|-----------|--------|
| Code | ✅ Complete (4 Python modules, ~1,100 lines) |
| Documentation | ✅ Complete |
| Git commits | ✅ Committed to workspace |
| Arduino credentials | ⏳ Waiting for Shawn |
| First test run | ⏳ Pending credentials |

---

## What Was Built

### 1. Arduino Collector (`scripts/arduino_collector.py`)
**Purpose:** Connect to Arduino IoT Cloud API and fetch sensor data

**Key Features:**
- OAuth2 authentication with automatic token refresh (tokens expire every 300 seconds)
- Fetches all Things and their Properties (variables)
- Gets current values and metadata
- Supports historical data queries (configurable time range)

**Dependencies:** `arduino-iot-client`, `oauthlib`, `requests-oauthlib`

**Main Methods:**
- `get_things()` — List all available Things
- `get_properties(thing_id)` — Get all variables for a Thing
- `collect_all_data(hours_back=24)` — Fetch everything

---

### 2. Report Generator (`scripts/report_generator.py`)
**Purpose:** Convert raw IoT data to human-readable Markdown reports

**Output Format:**
```markdown
# 🌡️ Arduino IoT Sensor Report

**Report Generated:** 2026-03-14 04:20:00
**Data Range:** 2026-03-14T00:00:00 → 2026-03-14T04:20:00

## 📊 Summary
- Total Things Monitored: 2
- Total Properties: 5

## 📡 Thing Details

### Thing: `my-sensor-device`

| Property | Type | Last Value | Updated |
|----------|------|------------|---------|
| Temperature (temp) | FLOAT | 23.50 | 04:15 |
| Humidity (humidity) | FLOAT | 65.00 | 04:15 |
```

**File Structure:**
- Reports saved to `reports/YYYY-MM-DD/sensor-report-HHMM.md`
- Each report includes summary table + collapsible raw JSON

---

### 3. Git Publisher (`scripts/git_publisher.py`)
**Purpose:** Automate git operations

**Features:**
- Auto-detects git repository root
- Stages specific files or all changes
- Creates commits with descriptive messages
- Pushes to remote (origin/main by default)
- Pulls latest changes before pushing (optional)

**Safety:**
- Checks for changes before committing (won't create empty commits)
- Returns commit hash for tracking
- Configurable remote and branch names

---

### 4. Pipeline Orchestrator (`scripts/run_pipeline.py`)
**Purpose:** Main entry point — coordinates everything

**Usage:**
```bash
# Check if everything is set up
python scripts/run_pipeline.py --check

# Dry run (collect + generate, no git push)
python scripts/run_pipeline.py --dry-run

# Full run
python scripts/run_pipeline.py

# Schedule automation
python scripts/run_pipeline.py --schedule hourly        # Every hour
python scripts/run_pipeline.py --schedule every-6-hours # Every 6 hours
python scripts/run_pipeline.py --schedule daily         # Daily at 9 AM
```

**What It Does:**
1. Collects data from all configured Things
2. Generates timestamped markdown report
3. Creates git commit with data summary
4. Pushes to GitHub
5. Returns structured results (success/failure, paths, commit hash)

---

## File Structure

```
arduino-iot-pipeline/
├── config/
│   ├── arduino_iot_config.json          ⏳ NEEDS: Your credentials
│   └── arduino_iot_config.json.template ✅ Template provided
├── scripts/
│   ├── run_pipeline.py                  ✅ Main entry point
│   ├── arduino_collector.py             ✅ IoT Cloud API client
│   ├── report_generator.py              ✅ Markdown builder
│   └── git_publisher.py                 ✅ Git operations
├── reports/                             ✅ Output directory (auto-created)
├── requirements.txt                     ✅ Python dependencies
├── .gitignore                           ✅ Secrets protection
└── README.md                            ✅ Usage instructions
```

---

## What You Need to Provide (To Unlock)

### 1. Arduino Cloud API Credentials
**Where to get:** https://cloud.arduino.cc/ → API Keys → Create

```json
{
  "client_id": "YOUR_CLIENT_ID_HERE",
  "client_secret": "YOUR_CLIENT_SECRET_HERE",
  "thing_ids": ["YOUR_THING_ID_1"]
}
```

**Important:** Save the Client Secret immediately — Arduino only shows it once (as a PDF).

### 2. Thing ID(s)
**Where to get:** Arduino Cloud → Your Thing → Metadata tab

The Thing ID looks like: `f8a9b2c3-d4e5-6789-abcd-ef0123456789`

You can monitor multiple Things by adding multiple IDs to the list.

### 3. GitHub Repository
**Options:**
- Use existing repo (provide URL)
- Create new repo (I can help with this)
- Use this workspace's repo (if you want reports in your main workspace)

### 4. Schedule Preference
**Options:**
- `hourly` — Every hour at :00
- `every-6-hours` — At 00:00, 06:00, 12:00, 18:00
- `daily` — Every day at 9:00 AM
- Custom cron expression (if you have specific needs)

---

## Testing Procedures (When Ready)

### Step 1: Install Dependencies
```bash
cd arduino-iot-pipeline
pip install -r requirements.txt
```

### Step 2: Configure Credentials
```bash
cp config/arduino_iot_config.json.template config/arduino_iot_config.json
# Edit the file with your credentials
nano config/arduino_iot_config.json
```

### Step 3: Verify Setup
```bash
python scripts/run_pipeline.py --check
```

Expected output:
```
Setup Checklist:
----------------------------------------
  ✓ config_file
  ✓ git_repo
  ✓ python_deps
  ✓ git_remote
----------------------------------------
✓ All checks passed! Ready to run.
```

### Step 4: Dry Run (Test Without Git Push)
```bash
python scripts/run_pipeline.py --dry-run
```

This will:
- Connect to Arduino Cloud
- Fetch your sensor data
- Generate a report
- Save it locally
- **NOT push to GitHub**

Check the generated report at: `reports/YYYY-MM-DD/sensor-report-HHMM.md`

### Step 5: Full Test
```bash
python scripts/run_pipeline.py
```

This will:
- Do everything from Step 4
- Commit the report
- Push to GitHub

### Step 6: Set Up Automation
```bash
python scripts/run_pipeline.py --schedule hourly
```

Verify cron job:
```bash
crontab -l
```

---

## Troubleshooting Guide

### "Config file not found"
**Cause:** `config/arduino_iot_config.json` doesn't exist
**Fix:** Copy from template and add credentials
```bash
cp config/arduino_iot_config.json.template config/arduino_iot_config.json
```

### "Failed to get access token"
**Causes:**
- Wrong Client ID or Client Secret
- Credentials have spaces or extra characters
- API key was deleted in Arduino Cloud

**Fix:** Regenerate API key in Arduino Cloud, copy carefully

### "Unauthorized" when fetching data
**Cause:** Thing ID doesn't exist or API key doesn't have access
**Fix:** Verify Thing ID in Arduino Cloud → Thing → Metadata tab

### "Not in a git repository"
**Cause:** Directory isn't a git repo
**Fix:**
```bash
git init
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

### "No remote configured"
**Fix:**
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

### "Permission denied" when pushing
**Cause:** No write access to repo, or not authenticated
**Fix:**
- For HTTPS: Use personal access token instead of password
- For SSH: Ensure SSH key is set up

---

## Git History

| Commit | Description |
|--------|-------------|
| `a251b68` | Add Arduino IoT → GitHub pipeline (fully built, pending credentials) |
| `3e326fa` | Add Arduino IoT pipeline to active projects in MEMORY.md |
| `07486e4` | Update IDENTITY.md: remove 'dummy' and 'first day' language per user correction |
| `eeeed2b` | Update signature line: Orthia + California timestamp |

---

## Notes for Future Discussion

### Potential Enhancements (Discuss Later)
1. **Threshold Alerts** — Send Telegram notification if temperature/humidity exceeds limits
2. **Data Visualization** — Add charts to reports (matplotlib/plotly)
3. **Historical Analysis** — Compare current values to averages
4. **Multiple Output Formats** — JSON, CSV, PDF in addition to Markdown
5. **Data Retention** — Auto-delete old reports after N days
6. **Health Checks** — Alert if a sensor stops reporting
7. **Dashboard** — Simple web dashboard to view latest data

### Security Considerations
- Config file is gitignored — credentials won't be committed
- OAuth2 tokens expire every 5 minutes — automatically refreshed
- Consider using environment variables instead of JSON for credentials (discuss if preferred)

### Architecture Decisions
- **Why Arduino IoT Cloud?** You mentioned it specifically; official Python client exists
- **Why Markdown?** Human-readable, git-diffable, works on GitHub
- **Why Cron?** Simple, reliable, no external dependencies
- **Why local execution?** Arduino IoT Cloud API requires credentials — running locally keeps secrets secure

---

## Related Files

- `MEMORY.md` — Added to active projects section
- `IDENTITY.md` — Signature line updated during this session
- `SOUL.md` — No changes
- `USER.md` — No changes

---

## Next Steps (When You're Ready)

1. Gather Arduino Cloud credentials
2. Decide on GitHub repository location
3. Choose schedule preference
4. Run the test procedures above
5. Iterate if needed

**Just ask:** "Let's test the Arduino pipeline" and I'll know exactly what you mean.

---

*Documented for future reference. All details preserved.*
