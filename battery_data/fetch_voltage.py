#!/usr/bin/env python3
"""
Battery Voltage Monitor - Arduino IoT Cloud
Fetches voltage reading from dashboard and logs to CSV
"""

import asyncio
import csv
import os
from datetime import datetime
from playwright.async_api import async_playwright

# Configuration
DASHBOARD_URL = "https://app.arduino.cc/dashboards/df883ac4-b65c-40b2-9a96-b3b01adffe1d"
LOGIN_URL = "https://login.arduino.cc/login"
CSV_FILE = "/root/.openclaw/workspace/battery_data/voltage_log.csv"
CREDENTIALS_FILE = "/root/.openclaw/workspace/.arduino_credentials"
SCREENSHOT_DIR = "/root/.openclaw/workspace/battery_data"

def get_credentials():
    """Read credentials from file or use defaults"""
    username = "orthia@aiconversations.info"
    password = "Orthia111!"
    
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, 'r') as f:
                lines = f.read().strip().split('\n')
                for line in lines:
                    if line.startswith('username:'):
                        username = line.split(':', 1)[1].strip()
                    elif line.startswith('password:'):
                        password = line.split(':', 1)[1].strip()
        except Exception as e:
            print(f"Warning: Could not read credentials file: {e}")
    
    return username, password

async def fetch_voltage():
    """Fetch voltage from Arduino IoT Cloud dashboard"""
    username, password = get_credentials()
    
    async with async_playwright() as p:
        # Launch browser in headless mode
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        try:
            print("Navigating to Arduino IoT Cloud dashboard...")
            await page.goto(DASHBOARD_URL, timeout=60000)
            
            # Wait for page to load
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)
            
            # Take screenshot of initial page
            await page.screenshot(path=f'{SCREENSHOT_DIR}/step1_initial.png')
            print(f"Initial page screenshot saved")
            
            # Check current URL - if we're on login page, handle login
            current_url = page.url
            print(f"Current URL: {current_url}")
            
            if 'login' in current_url.lower() or 'auth' in current_url.lower():
                print("On login page, entering credentials...")
                
                # Try multiple selectors for email field
                email_selectors = [
                    'input[type="email"]',
                    'input[name="username"]',
                    'input[name="email"]',
                    'input[id*="email" i]',
                    'input[id*="username" i]',
                    'input[placeholder*="email" i]',
                    'input[placeholder*="Email" i]',
                    'input[inputmode="email"]',
                ]
                
                email_field = None
                for selector in email_selectors:
                    try:
                        email_field = await page.wait_for_selector(selector, timeout=5000)
                        if email_field:
                            print(f"Found email field: {selector}")
                            break
                    except:
                        continue
                
                if not email_field:
                    # Try to find any input field that might be for email
                    inputs = await page.query_selector_all('input')
                    for inp in inputs:
                        input_type = await inp.get_attribute('type') or ''
                        if input_type in ['email', 'text', '']:
                            email_field = inp
                            print(f"Found potential email field by type: {input_type}")
                            break
                
                if email_field:
                    await email_field.fill(username)
                    print("Email entered")
                else:
                    raise Exception("Could not find email input field")
                
                # Try multiple selectors for password field
                password_selectors = [
                    'input[type="password"]',
                    'input[name="password"]',
                    'input[id*="password" i]',
                    'input[placeholder*="password" i]',
                    'input[placeholder*="Password" i]',
                ]
                
                password_field = None
                for selector in password_selectors:
                    try:
                        password_field = await page.wait_for_selector(selector, timeout=5000)
                        if password_field:
                            print(f"Found password field: {selector}")
                            break
                    except:
                        continue
                
                if password_field:
                    await password_field.fill(password)
                    print("Password entered")
                else:
                    raise Exception("Could not find password input field")
                
                # Take screenshot before clicking login
                await page.screenshot(path=f'{SCREENSHOT_DIR}/step2_filled.png')
                
                # Try multiple selectors for login button
                login_button_selectors = [
                    'button[type="submit"]',
                    'button:has-text("Log in")',
                    'button:has-text("Login")',
                    'button:has-text("Sign in")',
                    'input[type="submit"]',
                    'button[id*="login" i]',
                    'button[id*="submit" i]',
                    'a:has-text("Log in")',
                ]
                
                login_button = None
                for selector in login_button_selectors:
                    try:
                        login_button = await page.wait_for_selector(selector, timeout=3000)
                        if login_button:
                            print(f"Found login button: {selector}")
                            break
                    except:
                        continue
                
                if login_button:
                    await login_button.click()
                    print("Clicked login button")
                else:
                    # Try pressing Enter on password field
                    await password_field.press('Enter')
                    print("Pressed Enter to submit")
                
                # Wait for navigation after login
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(5)
                
                # Take screenshot after login attempt
                await page.screenshot(path=f'{SCREENSHOT_DIR}/step3_after_login.png')
                print(f"After login URL: {page.url}")
            
            # Check if we're on the dashboard
            if 'dashboard' not in page.url.lower():
                print(f"Warning: Not on dashboard page. Current URL: {page.url}")
            
            # Look for the 1H button and click it
            print("Looking for 1H time period button...")
            
            # Try multiple selectors for the 1H button
            time_buttons = [
                'button:has-text("1 H")',
                'button:has-text("1H")',
                'button:has-text("1h")',
                'button:has-text("1 hour")',
                '[data-testid*="1H" i]',
                '[data-testid*="1h" i]',
                'button[aria-label*="1 hour" i]',
                'button[aria-label*="1H" i]',
                'button:has-text("1H")',
                'text="1 H"',
                'text="1H"',
            ]
            
            one_h_button = None
            for selector in time_buttons:
                try:
                    one_h_button = await page.wait_for_selector(selector, timeout=3000)
                    if one_h_button:
                        print(f"Found 1H button with selector: {selector}")
                        break
                except:
                    continue
            
            # If not found by text, look for button group with time options
            if not one_h_button:
                print("Searching for time buttons by context...")
                # Look for buttons that might be time selectors
                all_buttons = await page.query_selector_all('button')
                for btn in all_buttons:
                    btn_text = await btn.text_content()
                    if btn_text and ('1' in btn_text and ('H' in btn_text.upper() or 'h' in btn_text)):
                        one_h_button = btn
                        print(f"Found 1H button by text content: '{btn_text}'")
                        break
            
            if one_h_button:
                await one_h_button.click()
                print("Clicked 1H button, waiting for data to update...")
                await asyncio.sleep(3)
            else:
                print("Could not find 1H button, proceeding with current view...")
            
            # Take screenshot of dashboard
            await page.screenshot(path=f'{SCREENSHOT_DIR}/step4_dashboard.png', full_page=True)
            print("Dashboard screenshot saved")
            
            # Try to find the voltage value
            print("Searching for voltage value...")
            
            voltage_value = None
            
            # Method 1: Look for elements with specific selectors
            voltage_selectors = [
                '[class*="value" i]',
                '[class*="voltage" i]',
                '[class*="number" i]',
                '[class*="metric" i]',
                '[data-testid*="value" i]',
                '[data-testid*="voltage" i]',
                'text=/\\d+\\.\\d{3}/',
            ]
            
            for selector in voltage_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for elem in elements:
                        text = await elem.text_content()
                        if text:
                            text = text.strip()
                            # Look for voltage pattern (10-15V range)
                            import re
                            match = re.search(r'(\d{2}\.\d{3})', text)
                            if match:
                                val = float(match.group(1))
                                if 10 <= val <= 15:  # Valid battery voltage range
                                    voltage_value = val
                                    print(f"Found voltage: {voltage_value} V in element: {selector}")
                                    break
                    if voltage_value:
                        break
                except Exception as e:
                    continue
            
            # Method 2: Search all text on page for voltage pattern
            if not voltage_value:
                print("Searching page content for voltage pattern...")
                page_text = await page.content()
                import re
                # Look for voltage patterns in the HTML
                voltage_patterns = [
                    r'(\d{2}\.\d{3})',  # e.g., 13.691
                    r'(\d{2}\.\d{2})',  # e.g., 13.69
                ]
                
                for pattern in voltage_patterns:
                    matches = re.findall(pattern, page_text)
                    for match in matches:
                        val = float(match)
                        if 10 <= val <= 15:
                            voltage_value = val
                            print(f"Found voltage from page content: {voltage_value} V")
                            break
                    if voltage_value:
                        break
            
            # Method 3: Look for specific widget/chart values
            if not voltage_value:
                print("Searching for widget values...")
                # Get all divs and spans
                elements = await page.query_selector_all('div, span, p, h1, h2, h3, h4, h5, h6')
                import re
                for elem in elements:
                    try:
                        text = await elem.text_content()
                        if text:
                            text = text.strip()
                            # Look for numbers that could be voltage
                            match = re.search(r'^(\d{2}\.\d{2,3})$', text)
                            if match:
                                val = float(match.group(1))
                                if 10 <= val <= 15:
                                    voltage_value = val
                                    print(f"Found voltage in element text: {voltage_value} V")
                                    break
                    except:
                        continue
            
            await browser.close()
            
            return voltage_value
                
        except Exception as e:
            # Take error screenshot
            try:
                await page.screenshot(path=f'{SCREENSHOT_DIR}/error_screenshot.png')
            except:
                pass
            await browser.close()
            print(f"Error during browser automation: {e}")
            raise

def log_voltage(voltage):
    """Log voltage to CSV file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Create file with headers if it doesn't exist
    file_exists = os.path.exists(CSV_FILE)
    
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'voltage'])
        writer.writerow([timestamp, f"{voltage:.3f}"])
    
    return timestamp

def main():
    """Main function"""
    try:
        voltage = asyncio.run(fetch_voltage())
        
        if voltage is not None:
            timestamp = log_voltage(voltage)
            print(f"\nSUCCESS: Voltage reading logged")
            print(f"Timestamp: {timestamp}")
            print(f"Voltage: {voltage:.3f} V")
            
            # Print the report table
            print(f"\n╔══════════════════════════════════════╗")
            print(f"║  BATTERY VOLTAGE REPORT - 1H VIEW    ║")
            print(f"╠══════════════════════════════════════╣")
            print(f"║  Timestamp: {timestamp:<20}   ║")
            print(f"║  Voltage:   {voltage:.3f} V{'':<11}              ║")
            print(f"║  Status:    OK{'':<23}       ║")
            print(f"╚══════════════════════════════════════╝")
            
            return 0
        else:
            print("\nERROR: Could not extract voltage value from dashboard")
            
            # Print error report
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n╔══════════════════════════════════════╗")
            print(f"║  BATTERY VOLTAGE REPORT - 1H VIEW    ║")
            print(f"╠══════════════════════════════════════╣")
            print(f"║  Timestamp: {timestamp:<20}   ║")
            print(f"║  Voltage:   N/A{'':<22}       ║")
            print(f"║  Status:    ERROR{'':<20}       ║")
            print(f"╚══════════════════════════════════════╝")
            
            return 1
            
    except Exception as e:
        print(f"\nERROR: {e}")
        
        # Print error report
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n╔══════════════════════════════════════╗")
        print(f"║  BATTERY VOLTAGE REPORT - 1H VIEW    ║")
        print(f"╠══════════════════════════════════════╣")
        print(f"║  Timestamp: {timestamp:<20}   ║")
        print(f"║  Voltage:   N/A{'':<22}       ║")
        print(f"║  Status:    ERROR{'':<20}       ║")
        print(f"╚══════════════════════════════════════╝")
        
        return 1

if __name__ == "__main__":
    exit(main())
