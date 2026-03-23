
from playwright.sync_api import sync_playwright
import os
import csv
from datetime import datetime

# Credentials
USERNAME = "orthia@aiconversations.info"
PASSWORD = "Orthia111!"
DASHBOARD_URL = "https://app.arduino.cc/dashboards/df883ac4-b65c-40b2-9a96-b3b01adffe1d"
CSV_FILE = "/root/.openclaw/workspace/battery_data/voltage_log.csv"

# Ensure directory exists
os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)

def main():
    voltage = None
    status = "ERROR"
    error_msg = ""
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = context.new_page()
            
            print("Navigating to Arduino login page...")
            page.goto("https://login.arduino.cc/login", wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)
            
            # Handle cookie consent if present
            print("Checking for cookie consent...")
            cookie_selectors = [
                'button:has-text("ACCEPT")',
                'button:has-text("Accept")',
                '[data-testid*="cookie"] button',
                '.cookie-consent button',
            ]
            for selector in cookie_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        print("Accepting cookies...")
                        page.locator(selector).first.click()
                        page.wait_for_timeout(1000)
                        break
                except:
                    pass
            
            # Take screenshot of login page
            page.screenshot(path="/root/.openclaw/workspace/battery_data/login_page.png")
            
            print("Filling email...")
            # Try various selectors for email field
            email_selectors = [
                'input[type="email"]',
                'input[name="email"]',
                'input[name="username"]',
                'input[id*="email"]',
                'input[placeholder*="email" i]',
            ]
            
            for selector in email_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        print(f"Found email field: {selector}")
                        page.locator(selector).first.fill(USERNAME)
                        break
                except Exception as e:
                    print(f"  Failed: {e}")
                    continue
            else:
                # Print all input fields for debugging
                inputs = page.locator('input').all()
                print(f"Found {len(inputs)} input fields:")
                for i, inp in enumerate(inputs):
                    try:
                        print(f"  {i}: type={inp.get_attribute('type')}, name={inp.get_attribute('name')}, id={inp.get_attribute('id')}")
                    except:
                        pass
            
            # Click continue/next to go to password screen
            print("Clicking continue...")
            continue_selectors = [
                'button[type="submit"]',
                'button:has-text("Continue")',
                'button:has-text("Next")',
                'button:has-text("Sign in")',
            ]
            
            for selector in continue_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        print(f"Clicking: {selector}")
                        page.locator(selector).first.click()
                        break
                except Exception as e:
                    print(f"  Failed: {e}")
            
            page.wait_for_timeout(3000)
            page.screenshot(path="/root/.openclaw/workspace/battery_data/password_page.png")
            
            # Now fill password
            print("Filling password...")
            password_selectors = [
                'input[type="password"]',
                'input[name="password"]',
                'input[id*="password"]',
            ]
            
            for selector in password_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        print(f"Found password field: {selector}")
                        page.locator(selector).first.fill(PASSWORD)
                        break
                except Exception as e:
                    print(f"  Failed: {e}")
            
            # Click sign in
            print("Clicking sign in...")
            signin_selectors = [
                'button[type="submit"]',
                'button:has-text("Sign in")',
                'button:has-text("Log in")',
            ]
            
            for selector in signin_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        print(f"Clicking: {selector}")
                        page.locator(selector).first.click()
                        break
                except Exception as e:
                    print(f"  Failed: {e}")
            
            print("Waiting for login to complete...")
            page.wait_for_timeout(5000)
            page.wait_for_load_state("networkidle", timeout=30000)
            
            # Navigate to dashboard
            print(f"Navigating to dashboard: {DASHBOARD_URL}")
            page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000)
            
            page.screenshot(path="/root/.openclaw/workspace/battery_data/dashboard_before.png")
            
            # Look for and click "1 H" button
            print("Looking for 1H button...")
            time_selectors = [
                'text=1 H',
                'button:has-text("1 H")',
                'button:has-text("1H")',
                '[role="button"]:has-text("1 H")',
                '[data-testid*="1h" i]',
            ]
            
            for selector in time_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        print(f"Found 1H button: {selector}")
                        page.locator(selector).first.click()
                        page.wait_for_timeout(3000)
                        break
                except Exception as e:
                    print(f"  Failed: {e}")
            
            page.wait_for_timeout(3000)
            page.screenshot(path="/root/.openclaw/workspace/battery_data/dashboard_1h.png")
            
            # Extract voltage value
            print("Extracting voltage...")
            import re
            
            # Get visible text from the page
            page_text = page.inner_text("body")
            
            # Look for voltage pattern (XX.XXX)
            voltage_matches = re.findall(r'(\d{2}\.\d{3})', page_text)
            print(f"Found potential voltage matches: {voltage_matches}")
            
            for v in voltage_matches:
                val = float(v)
                if 10 <= val <= 20:  # Reasonable battery voltage range
                    voltage = v
                    print(f"Found voltage: {voltage}V")
                    status = "OK"
                    break
            
            # If not found in text, try HTML content
            if not voltage:
                page_content = page.content()
                voltage_matches = re.findall(r'(\d{2}\.\d{3})', page_content)
                for v in voltage_matches:
                    val = float(v)
                    if 10 <= val <= 20:
                        voltage = v
                        print(f"Found voltage from HTML: {voltage}V")
                        status = "OK"
                        break
            
            browser.close()
            
    except Exception as e:
        error_msg = str(e)
        import traceback
        traceback.print_exc()
        print(f"Error: {error_msg}")
    
    # Log to CSV
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create CSV with headers if it doesn't exist
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'voltage'])
    
    # Append the reading
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, voltage if voltage else 'ERROR'])
    
    # Print results
    print(f"\n{'='*40}")
    print(f"Timestamp: {timestamp}")
    if voltage:
        print(f"Voltage: {voltage}V")
    else:
        print(f"Voltage: ERROR - {error_msg}")
    print(f"Status: {status}")
    print(f"{'='*40}")
    
    return voltage, timestamp, status

if __name__ == "__main__":
    main()
