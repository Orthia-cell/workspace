#!/usr/bin/env python3
"""Arduino IoT Cloud Dashboard Viewer - Improved Login"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time

USERNAME = "orthia@aiconversations.info"
PASSWORD = "Orthia111!"
DASHBOARD_URL = "https://app.arduino.cc/dashboards/df883ac4-b65c-40b2-9a96-b3b01adffe1d"

def wait_and_screenshot(page, name, delay=3):
    """Wait and take screenshot."""
    time.sleep(delay)
    path = f"/root/.openclaw/workspace/battery_analysis/{name}.png"
    page.screenshot(path=path, full_page=True)
    print(f"📸 Screenshot: {path}")
    return path

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = context.new_page()
        
        print("=" * 70)
        print("ARDUINO IOT CLOUD - BATTERY DASHBOARD ANALYSIS")
        print("=" * 70)
        
        try:
            # Step 1: Navigate to login page
            print("\n[1/7] Navigating to Arduino login...")
            page.goto("https://login.arduino.cc/login", wait_until="networkidle")
            wait_and_screenshot(page, "01_login_page")
            
            # Step 2: Fill credentials
            print("[2/7] Entering credentials...")
            
            # Find and fill username
            username_field = page.locator('input[type="email"], input[name="username"], #username, input[placeholder*="mail" i]').first
            username_field.wait_for(state="visible", timeout=10000)
            username_field.fill(USERNAME)
            print(f"      ✓ Username entered: {USERNAME}")
            
            # Click continue/next if present
            continue_btn = page.locator('button:has-text("Continue"), button:has-text("Next"), input[type="submit"]').first
            if continue_btn.count() > 0 and continue_btn.is_visible():
                continue_btn.click()
                time.sleep(2)
            
            # Find and fill password
            password_field = page.locator('input[type="password"], input[name="password"], #password').first
            password_field.wait_for(state="visible", timeout=10000)
            password_field.fill(PASSWORD)
            print("      ✓ Password entered")
            
            wait_and_screenshot(page, "02_credentials_filled")
            
            # Step 3: Submit login
            print("[3/7] Submitting login...")
            submit_btn = page.locator('button[type="submit"], button:has-text("Sign in"), button:has-text("Login"), input[type="submit"]').first
            submit_btn.click()
            
            # Wait for navigation
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except PlaywrightTimeout:
                print("      ⚠ Network idle timeout, continuing...")
            
            time.sleep(5)
            wait_and_screenshot(page, "03_after_login")
            print(f"      ✓ Current URL: {page.url}")
            
            # Step 4: Navigate to dashboard
            print("[4/7] Loading dashboard...")
            page.goto(DASHBOARD_URL, wait_until="networkidle")
            time.sleep(5)
            wait_and_screenshot(page, "04_dashboard_loaded")
            print(f"      ✓ Dashboard URL: {page.url}")
            print(f"      ✓ Page title: {page.title()}")
            
            # Step 5: Look for 1D button and time controls
            print("[5/7] Looking for time range controls...")
            
            # Get all button text
            buttons = page.locator('button').all()
            button_texts = []
            for btn in buttons:
                try:
                    text = btn.text_content()
                    if text:
                        button_texts.append(text.strip())
                except:
                    pass
            
            print(f"      Found {len(button_texts)} buttons")
            time_buttons = [t for t in button_texts if any(x in t for x in ['1D', '7D', '30D', '1D', 'Day', 'Hour'])]
            print(f"      Time-related buttons: {time_buttons[:10]}")
            
            # Try to click 1D
            one_d_selectors = [
                'button:has-text("1 D")',
                'button:has-text("1D")', 
                'text=1 D',
                '[data-testid*="1d"]',
                'button >> text=/1\\s*D/i'
            ]
            
            clicked = False
            for selector in one_d_selectors:
                try:
                    elem = page.locator(selector).first
                    if elem.count() > 0 and elem.is_visible():
                        elem.click()
                        print(f"      ✓ Clicked: {selector}")
                        clicked = True
                        time.sleep(3)
                        break
                except Exception as e:
                    continue
            
            if not clicked:
                print("      ⚠ Could not find 1D button")
            
            wait_and_screenshot(page, "05_1d_view")
            
            # Step 6: Extract voltage data
            print("[6/7] Extracting voltage data...")
            
            # Get all text on page
            page_text = page.inner_text('body')
            
            # Look for voltage values
            import re
            numbers = re.findall(r'\d+\.\d{2,4}', page_text)
            voltage_candidates = [n for n in numbers if 10 <= float(n) <= 20]
            
            print(f"      Potential voltage readings: {voltage_candidates[:10]}")
            
            # Look for specific patterns
            voltage_value = None
            if voltage_candidates:
                voltage_value = voltage_candidates[0]
                print(f"      ✓ Most likely voltage: {voltage_value} V")
            
            # Step 7: Analyze page structure
            print("[7/7] Analyzing dashboard structure...")
            
            # Look for chart elements
            charts = page.locator('canvas, svg, .chart, [class*="chart"], [class*="graph"]').all()
            print(f"      Found {len(charts)} chart/graph elements")
            
            # Look for widget cards
            widgets = page.locator('[class*="widget"], [class*="card"], [class*="panel"]').all()
            print(f"      Found {len(widgets)} widget/card elements")
            
            # Get visible text summary
            visible_text = page_text[:2000]  # First 2000 chars
            
            print("\n" + "=" * 70)
            print("EXTRACTION RESULTS")
            print("=" * 70)
            print(f"\n📊 Current Voltage Reading: {voltage_value or 'N/A'} V")
            print(f"🔗 Dashboard URL: {page.url}")
            print(f"📄 Page Title: {page.title()}")
            print(f"\n📈 Chart Elements Found: {len(charts)}")
            print(f"🎛️ Widget Elements Found: {len(widgets)}")
            
            # Save analysis
            analysis_path = "/root/.openclaw/workspace/battery_analysis/extraction_report.txt"
            with open(analysis_path, 'w') as f:
                f.write("ARDUINO IOT CLOUD DASHBOARD EXTRACTION REPORT\n")
                f.write("=" * 70 + "\n\n")
                f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"URL: {page.url}\n")
                f.write(f"Title: {page.title()}\n\n")
                f.write(f"Voltage Reading: {voltage_value or 'N/A'} V\n\n")
                f.write("Voltage Candidates:\n")
                for v in voltage_candidates[:20]:
                    f.write(f"  - {v} V\n")
                f.write(f"\nButton Texts Found:\n")
                for btn in button_texts[:30]:
                    f.write(f"  - {btn}\n")
                f.write(f"\n--- Page Text Sample ---\n")
                f.write(visible_text[:3000])
            
            print(f"\n📄 Full report saved: {analysis_path}")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            wait_and_screenshot(page, "error_state")
        
        finally:
            browser.close()
        
        print("\n" + "=" * 70)
        print("ANALYSIS COMPLETE")
        print("=" * 70)

if __name__ == "__main__":
    main()
