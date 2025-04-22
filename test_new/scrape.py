import json
import os
import time
from playwright.sync_api import sync_playwright

SESSION_FILE = "session.json"
OUTPUT_FILE = "products.json"
LOGIN_URL = "http://localhost:5000/login"  # Replace with actual URL
USERNAME = "test"
PASSWORD = "test"

def save_storage(context):
    context.storage_state(path=SESSION_FILE)

def load_or_login(playwright):
    print("🌐 Launching browser...")
    time.sleep(1)  # Delay before launch
    browser = playwright.chromium.launch(headless=False)
    context = None

    if os.path.exists(SESSION_FILE):
        print("✅ Using existing session...")
        time.sleep(1)
        context = browser.new_context(storage_state=SESSION_FILE)
        page = context.new_page()
        page.goto("http://localhost:5000/dashboard")
        time.sleep(2)  # Delay after navigation
        if not page.locator("text='Logout'").is_visible():
            print("⚠️ Session expired. Logging in again.")
            time.sleep(1)
            os.remove(SESSION_FILE)
            context.close()
            return load_or_login(playwright)
    else:
        print("🔐 Logging in with credentials...")
        time.sleep(1)
        context = browser.new_context()
        page = context.new_page()
        page.goto(LOGIN_URL)
        time.sleep(1)
        page.fill("input[name='username']", USERNAME)
        time.sleep(0.5)  # Slight delay between inputs
        page.fill("input[name='password']", PASSWORD)
        time.sleep(0.5)
        page.click("button[type='submit']")
        page.wait_for_selector("text='Dashboard'", timeout=10000)
        time.sleep(2)  # Delay after successful login
        save_storage(context)

    return context

def navigate_to_product_table(page):
    print("🧭 Starting product wizard navigation...")
    time.sleep(1)

    # Set viewport size to ensure everything is visible
    page.set_viewport_size({"width": 1280, "height": 800})

    # Navigate to Tools page
    print("📊 Step 1: Navigating to Tools...")
    page.click("text='Tools'")
    time.sleep(2)

    try:
        # Step 1: Select Data Source
        print("📊 Selecting Data Source...")
        page.wait_for_selector("#step1", state="visible", timeout=5000)
        page.click("button:has-text('Local Database')")
        time.sleep(1)
        
        # Use JavaScript to ensure step visibility and click
        page.evaluate("""() => {
            document.querySelector('#step1').classList.add('active');
            document.querySelector('#step1 button[onclick*="nextStep"]').click();
        }""")
        time.sleep(1)

        # Step 2: Choose Category
        print("📂 Selecting Category...")
        page.wait_for_selector("#step2", state="visible", timeout=5000)
        page.click("button:has-text('Electronics')")
        time.sleep(1)
        
        # Use JavaScript for step 2 navigation
        page.evaluate("""() => {
            document.querySelector('#step2').classList.add('active');
            document.querySelector('#step2 button[onclick*="nextStep"]').click();
        }""")
        time.sleep(1)

        # Step 3: Select View Type
        print("👀 Selecting View Type...")
        page.wait_for_selector("#step3", state="visible", timeout=5000)
        page.click("button:has-text('Table View')")
        time.sleep(1)
        
        # Use JavaScript for step 3 navigation
        page.evaluate("""() => {
            document.querySelector('#step3').classList.add('active');
            document.querySelector('#step3 button[onclick*="nextStep"]').click();
        }""")
        time.sleep(1)

        # Step 4: View Products
        print("🎯 Viewing Products...")
        page.wait_for_selector("#step4", state="visible", timeout=5000)
        
        # Changed JavaScript to use proper selector
        page.evaluate("""() => {
            const viewBtn = Array.from(document.getElementsByTagName('button'))
                .find(btn => btn.textContent.includes('View Products'));
            if (viewBtn) viewBtn.click();
        }""")
        
        # Wait for table to appear
        page.wait_for_selector("table", state="visible", timeout=10000)
        time.sleep(2)

        print("✅ Completed wizard navigation to product table.")
        
    except Exception as e:
        # Take screenshot on error for debugging
        page.screenshot(path="error_screenshot.png")
        print(f"❌ Navigation failed: {str(e)}")
        print("📸 Screenshot saved as error_screenshot.png")
        raise

    return page

def extract_product_data(page):
    print("📊 Extracting product data...")
    all_products = []

    while True:
        # Wait for table to load
        page.wait_for_selector("table", timeout=5000)
        time.sleep(0.5)  # Added delay before reading table

        rows = page.query_selector_all("table tbody tr")
        for row in rows:
            cells = row.query_selector_all("td")
            if len(cells) >= 4:
                product = {
                    "name": cells[0].inner_text().strip(),
                    "sku": cells[1].inner_text().strip(),
                    "quantity": cells[2].inner_text().strip(),
                    "price": cells[3].inner_text().strip()
                }
                all_products.append(product)
                time.sleep(0.2)  # Added small delay between rows

        # Check if next button exists and is clickable
        try:
            next_button = page.locator("button:has-text('Next')")
            if next_button.count() == 0 or not next_button.is_visible() or not next_button.is_enabled():
                break
            print("   Loading next page...")
            next_button.click()
            time.sleep(1.5)  # Increased delay after pagination
        except Exception as e:
            print(f"⚠️ Pagination stopped (no next button or error): {e}")
            break

    print(f"✅ Extracted {len(all_products)} products.")
    return all_products


def save_to_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"📁 Saved to {filename}")

def main():
    with sync_playwright() as playwright:
        context = load_or_login(playwright)
        page = context.new_page()
        page.goto("http://localhost:5000/dashboard")
        navigate_to_product_table(page)
        products = extract_product_data(page)
        save_to_json(products, OUTPUT_FILE)
        # context.close()

if __name__ == "__main__":
    main()
    print("🚀 Script completed.")