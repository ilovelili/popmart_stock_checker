#!/usr/bin/env python3
# Debug script to see what buttons/text POPMART actually shows

import sys
from playwright.sync_api import sync_playwright

def debug_page(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Show browser
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)  # Wait longer
        
        print("=== All button texts found ===")
        for selector in ["button", "[role='button']", "a", ".btn", ".button"]:
            try:
                elements = page.locator(selector).all()
                for i, el in enumerate(elements[:20]):  # Limit to first 20
                    try:
                        text = el.text_content()
                        if text and text.strip():
                            print(f"{selector}[{i}]: '{text.strip()}'")
                    except:
                        pass
            except:
                pass
        
        print("\n=== Page title ===")
        print(page.title())
        
        input("Press Enter to close browser...")
        browser.close()

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.popmart.com/jp/products/3884"
    debug_page(url)