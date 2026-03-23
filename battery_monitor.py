#!/usr/bin/env python3
"""
Battery Voltage Monitor - Arduino IoT Cloud Scraper
"""
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import os
import sys
import re

# Configuration
DASHBOARD_URL = "https://app.arduino.cc/dashboards/df883ac4-b65c-40b2-9a96-b3b01adffe1d"
CREDENTIALS_FILE = "/root/.openclaw/workspace/.arduino_credentials"
LOG_FILE = "/root/.openclaw/workspace/battery_data/voltage_log.csv"

async def get_credentials():
    """Read credentials from file in KEY=VALUE format"""
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            content = f.read()
            
        # Parse KEY=VALUE format
        username = "orthia@aiconversations.info"  # default
        password = "Orthia111!"  # default
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('ARDUINO_IOT_USERNAME='):
                username = line.split('=', 1)[1].strip()
            elif line.startswith('ARDUINO_IOT_PASSWORD='):
                password = line.split('=', 1)[1].strip()
        
        print(f"Using username: {username}")
        return username, password
    except Exception as e:
        print(f"Warning: Could not read credentials file: {e}")
        return "orthia@aiconversations.info", "Orthia111!"

async def log_voltage(voltage, status="OK"):
    """Log voltage to CSV file"""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as f:
            f.write("timestamp,voltage\n")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a') as f:
        f.write(f"{timestamp},{voltage}\n")
    
    return timestamp

async def get_battery_voltage():
    """Main function to get battery voltage from Arduino IoT Cloud"""
    username, password = await get_credentials()
    voltage = None
    error_msg = None
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        try:
            print("Navigating to Arduino IoT Cloud login...")
            await page.goto("https://app.arduino.cc/", wait_until="networkidle")
            await asyncio.sleep(3)
            
            # Look for login button and click it
            print("Looking for login button...")
            try:
                login_btn = await page.wait_for_selector('a[href*="login"], button:has-text("Log in"), button:has-text("Sign in")', timeout=10000)
                if login_btn:
                    print("Found login button, clicking...")
                    await login_btn.click()
                    await asyncio.sleep(3)
            except:
                print("No login button found, might already be on login page")
            
            # Check current URL and navigate to login if needed
            current_url = page.url
            print(f"Current URL: {current_url}")
            
            if "login" not in current_url:
                print("Navigating directly to login page...")
                await page.goto("https://login.arduino.cc/login", wait_until="networkidle")
                await asyncio.sleep(3)
            
            print("Filling in login credentials...")
            
            # Find username/email field using placeholder
            try:
                username_field = await page.wait_for_selector('input[placeholder*="Username"], input[placeholder*="Email"], input[type="email"], input[name="username"], input[name="email"]', timeout=10000)
                await username_field.fill(username)
                print(f"Filled username: {username}")
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"Could not find username field: {e}")
            
            # Find password field
            try:
                password_field = await page.wait_for_selector('input[type="password"], input[name="password"], input[placeholder*="Password"]', timeout=10000)
                await password_field.fill(password)
                print("Filled password")
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"Could not find password field: {e}")
            
            # Find and click the SIGN IN button
            try:
                signin_btn = await page.wait_for_selector('button:has-text("SIGN IN"), button[type="submit"]', timeout=10000)
                print("Clicking SIGN IN button...")
                await signin_btn.click()
            except Exception as e:
                print(f"Could not find sign in button: {e}")
                # Try pressing Enter on password field
                try:
                    await password_field.press("Enter")
                    print("Pressed Enter to submit")
                except:
                    pass
            
            # Wait for login to complete
            print("Waiting for login to complete...")
            await asyncio.sleep(10)
            
            # Take screenshot after login attempt
            await page.screenshot(path="/root/.openclaw/workspace/battery_data/after_login.png")
            
            # Check if login was successful
            current_url = page.url
            print(f"URL after login: {current_url}")
            
            if "login" in current_url:
                print("ERROR: Still on login page - login failed")
                # Check for error message
                error_elem = await page.query_selector('.error, [role="alert"], .text-danger, .form-error')
                if error_elem:
                    error_text = await error_elem.text_content()
                    print(f"Login error message: {error_text}")
                error_msg = "Login failed - still on login page"
            else:
                print("Login appears successful!")
            
            # Navigate to dashboard
            print("Navigating to dashboard...")
            await page.goto(DASHBOARD_URL, wait_until="networkidle")
            await asyncio.sleep(5)
            
            # Take screenshot of dashboard
            await page.screenshot(path="/root/.openclaw/workspace/battery_data/dashboard.png")
            print("Dashboard screenshot saved")
            
            # Try to find and click the 1H button
            print("Looking for 1H time period button...")
            time_clicked = False
            
            # Look for time period buttons
            all_buttons = await page.query_selector_all('button, [role="button"]')
            for btn in all_buttons:
                try:
                    text = await btn.text_content()
                    if text:
                        text = text.strip()
                        if text in ["1 H", "1H", "1 h", "1h"] or (text == "1" and len(text) == 1):
                            print(f"Found 1H button with text: '{text}'")
                            await btn.click()
                            time_clicked = True
                            await asyncio.sleep(3)
                            break
                except:
                    continue
            
            if not time_clicked:
                print("Could not find 1H button, proceeding with current view...")
            
            # Extract voltage value
            print("Extracting voltage value...")
            
            # Method 1: Look for voltage in the visible page text
            page_text = await page.evaluate('() => document.body.innerText')
            lines = page_text.split('\n')
            
            for line in lines:
                line = line.strip()
                # Look for voltage pattern (XX.XXX)
                match = re.search(r'(\d{2,3}\.\d{2,4})', line)
                if match:
                    val = float(match.group(1))
                    # Valid battery voltage range (10-20V for typical battery)
                    if 10 <= val <= 20:
                        voltage = match.group(1)
                        print(f"Found voltage in page text: {voltage} V (line: '{line}')")
                        break
            
            # Method 2: Search in HTML content
            if not voltage:
                page_content = await page.content()
                matches = re.findall(r'(\d{2,3}\.\d{3})', page_content)
                for match in matches:
                    val = float(match)
                    if 10 <= val <= 20:
                        voltage = match
                        print(f"Found voltage in HTML: {voltage} V")
                        break
            
            # Method 3: Look for specific widget or value containers
            if not voltage:
                value_selectors = [
                    '[class*="value"]',
                    '[class*="metric"]',
                    '[data-testid*="value"]',
                    '[class*="widget"]',
                ]
                for selector in value_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        for elem in elements[:10]:
                            text = await elem.text_content()
                            if text:
                                match = re.search(r'(\d{2,3}\.\d{2,4})', text)
                                if match:
                                    val = float(match.group(1))
                                    if 10 <= val <= 20:
                                        voltage = match.group(1)
                                        print(f"Found voltage via selector {selector}: {voltage} V")
                                        break
                        if voltage:
                            break
                    except:
                        continue
            
            # Final screenshot
            await page.screenshot(path="/root/.openclaw/workspace/battery_data/final.png")
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error during automation: {e}")
            import traceback
            traceback.print_exc()
            await page.screenshot(path="/root/.openclaw/workspace/battery_data/error.png")
        
        finally:
            await browser.close()
    
    return voltage, error_msg

if __name__ == "__main__":
    voltage, error = asyncio.run(get_battery_voltage())
    
    if voltage:
        timestamp = asyncio.run(log_voltage(voltage))
        print(f"\n=== BATTERY VOLTAGE READING ===")
        print(f"Timestamp: {timestamp}")
        print(f"Voltage: {voltage} V")
        print(f"Status: OK")
        print(f"Logged to: {LOG_FILE}")
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        asyncio.run(log_voltage("ERROR", "FAILED"))
        print(f"\n=== ERROR ===")
        print(f"Timestamp: {timestamp}")
        print(f"Status: ERROR")
        if error:
            print(f"Error: {error}")
        print("Could not retrieve voltage reading")
