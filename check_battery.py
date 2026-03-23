#!/usr/bin/env python3
"""
Battery Voltage Monitor for Arduino IoT Cloud
Logs into Arduino IoT Cloud, navigates to dashboard, extracts voltage reading.
"""

import asyncio
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright

# Configuration
USERNAME = "orthia@aiconversations.info"
PASSWORD = "Orthia111!"
DASHBOARD_URL = "https://app.arduino.cc/dashboards/df883ac4-b65c-40b2-9a96-b3b01adffe1d"
OUTPUT_FILE = Path("/root/.openclaw/workspace/battery_data/voltage_log.csv")

def log_message(msg, level="INFO"):
    """Print timestamped log messages"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}")

async def check_battery_voltage():
    """Main function to check battery voltage from Arduino IoT Cloud"""
    
    voltage = None
    status = "ERROR"
    error_msg = None
    
    # Ensure output directory exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as p:
        browser = None
        try:
            log_message("Launching browser...")
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            # Step 1: Navigate to dashboard (will redirect to login)
            log_message(f"Navigating to dashboard...")
            await page.goto(DASHBOARD_URL, wait_until="domcontentloaded", timeout=30000)
            
            # Wait for page to load
            await asyncio.sleep(3)
            
            # Step 2: Check if we're on login page
            current_url = page.url
            log_message(f"Current URL: {current_url}")
            
            if "login" in current_url.lower() or "auth" in current_url.lower() or "id.arduino.cc" in current_url:
                log_message("Login page detected, attempting login...")
                
                # Try different possible selectors for email field
                email_selectors = [
                    'input[type="email"]',
                    'input[name="email"]',
                    'input[name="username"]',
                    'input[id*="email"]',
                    'input[id*="username"]',
                    'input[placeholder*="email"]',
                    'input[placeholder*="Email"]',
                ]
                
                # Wait for and fill email
                email_filled = False
                for selector in email_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=5000)
                        await page.fill(selector, USERNAME)
                        log_message(f"Email field found with selector: {selector}")
                        email_filled = True
                        break
                    except Exception as e:
                        continue
                
                if not email_filled:
                    # Try taking a screenshot to debug
                    await page.screenshot(path="/tmp/login_page.png")
                    log_message("Could not find email field. Screenshot saved to /tmp/login_page.png", "ERROR")
                    raise Exception("Email field not found")
                
                # Try different selectors for password field
                password_selectors = [
                    'input[type="password"]',
                    'input[name="password"]',
                    'input[id*="password"]',
                ]
                
                password_filled = False
                for selector in password_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=5000)
                        await page.fill(selector, PASSWORD)
                        log_message(f"Password field found with selector: {selector}")
                        password_filled = True
                        break
                    except Exception as e:
                        continue
                
                if not password_filled:
                    raise Exception("Password field not found")
                
                # Try to click submit button
                submit_selectors = [
                    'button[type="submit"]',
                    'button:has-text("Log in")',
                    'button:has-text("Login")',
                    'button:has-text("Sign in")',
                    'input[type="submit"]',
                ]
                
                submit_clicked = False
                for selector in submit_selectors:
                    try:
                        await page.click(selector, timeout=5000)
                        log_message(f"Submit button clicked with selector: {selector}")
                        submit_clicked = True
                        break
                    except Exception as e:
                        continue
                
                if not submit_clicked:
                    # Try pressing Enter
                    await page.press('input[type="password"]', "Enter")
                    log_message("Pressed Enter to submit")
                
                # Wait for login to complete
                log_message("Waiting for login to complete...")
                await asyncio.sleep(5)
                
                # Wait for redirect to dashboard
                try:
                    await page.wait_for_url("**/dashboards/**", timeout=30000)
                    log_message("Successfully logged in and redirected to dashboard")
                except Exception as e:
                    current_url = page.url
                    log_message(f"Current URL after login attempt: {current_url}")
                    if "login" in current_url.lower():
                        raise Exception("Login failed - still on login page")
            
            # Step 3: Navigate to the specific dashboard if needed
            if "df883ac4-b65c-40b2-9a96-b3b01adffe1d" not in page.url:
                log_message("Navigating to specific dashboard...")
                await page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(3)
            
            # Step 4: Look for and click the "1 H" button
            log_message("Looking for time period buttons...")
            
            # Try different selectors for the 1H button
            time_button_selectors = [
                'button:has-text("1 H")',
                'button:has-text("1H")',
                '[data-testid*="1H"]',
                '[data-testid*="1h"]',
                'button >> text=1 H',
                'button >> text=1H',
                'button:has-text("1 HOUR")',
                'button:has-text("1 HOUR")',
                '[role="button"]:has-text("1 H")',
                '[role="button"]:has-text("1H")',
            ]
            
            clicked_1h = False
            for selector in time_button_selectors:
                try:
                    # Check if button exists
                    button = await page.query_selector(selector)
                    if button:
                        await button.click()
                        log_message(f"Clicked 1H button with selector: {selector}")
                        clicked_1h = True
                        await asyncio.sleep(2)
                        break
                except Exception as e:
                    continue
            
            if not clicked_1h:
                log_message("Could not find 1H button, will try to extract from current view", "WARNING")
            
            # Step 5: Extract voltage value
            log_message("Extracting voltage value...")
            
            # Try different selectors for voltage display
            voltage_selectors = [
                '[data-testid*="voltage"]',
                '[data-testid*="Volt"]',
                '[class*="voltage"]',
                '[class*="value"]',
                'text=/\\d+\\.\\d+/',
                'span:has-text(".")',
                'div:has-text(".")',
            ]
            
            voltage_found = False
            for selector in voltage_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for elem in elements:
                        text = await elem.inner_text()
                        text = text.strip()
                        # Look for voltage-like numbers (typically 10-15V range for 12V batteries)
                        if text and '.' in text:
                            try:
                                val = float(text)
                                if 10 <= val <= 15:  # Reasonable battery voltage range
                                    voltage = val
                                    voltage_found = True
                                    log_message(f"Found voltage: {voltage} V")
                                    break
                            except ValueError:
                                continue
                    if voltage_found:
                        break
                except Exception as e:
                    continue
            
            # Alternative: Look for any text that looks like a voltage reading
            if not voltage_found:
                log_message("Trying alternative voltage extraction...")
                try:
                    # Get all text content and search for voltage pattern
                    page_content = await page.content()
                    import re
                    # Look for patterns like 13.691 or similar
                    voltage_pattern = r'(\d{2}\.\d{3})\s*[Vv]?(?:\s*<|$|\s)'
                    matches = re.findall(voltage_pattern, page_content)
                    if matches:
                        voltage = float(matches[0])
                        voltage_found = True
                        log_message(f"Found voltage via regex: {voltage} V")
                except Exception as e:
                    log_message(f"Regex extraction failed: {e}", "WARNING")
            
            if not voltage_found:
                raise Exception("Could not extract voltage value from dashboard")
            
            status = "OK"
            
        except Exception as e:
            error_msg = str(e)
            log_message(f"Error: {error_msg}", "ERROR")
            status = "ERROR"
            
        finally:
            if browser:
                await browser.close()
                log_message("Browser closed")
    
    # Step 6: Log to CSV
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create file with headers if it doesn't exist
    if not OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'voltage'])
        log_message(f"Created new CSV file: {OUTPUT_FILE}")
    
    # Append the reading
    with open(OUTPUT_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if voltage:
            writer.writerow([timestamp, f"{voltage:.3f}"])
        else:
            writer.writerow([timestamp, "ERROR"])
    
    log_message(f"Logged to CSV: {timestamp}, {voltage if voltage else 'ERROR'}")
    
    # Print report
    print("\n" + "="*50)
    print("BATTERY VOLTAGE REPORT - 1H VIEW")
    print("="*50)
    print(f"Timestamp: {timestamp}")
    print(f"Voltage:   {voltage:.3f} V" if voltage else f"Voltage:   N/A")
    print(f"Status:    {status}")
    if error_msg:
        print(f"Error:     {error_msg}")
    print("="*50 + "\n")
    
    return voltage, status, error_msg

if __name__ == "__main__":
    voltage, status, error = asyncio.run(check_battery_voltage())
    sys.exit(0 if status == "OK" else 1)
