# main.py
# Usage:
#   uv run popmart-stock-check https://www.popmart.com/jp/products/3884
# or:
#   uv run python main.py https://www.popmart.com/jp/products/3884

import sys, json, time, re, os, smtplib
from datetime import datetime, timezone, timedelta
from playwright.sync_api import sync_playwright
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

ADD_TO_CART_PATTERNS = [r"カートに追加", r"カートへ", r"Add to Cart", r"カート", r"購入"]
SOLD_OUT_PATTERNS    = [r"在庫切れ", r"SOLD OUT", r"売り切れ", r"完売", r"再入荷を通知"]

def jst_now_iso():
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst).isoformat(timespec="seconds")

def text_matches_any(text, patterns):
    t = (text or "").strip()
    return any(re.search(p, t, re.IGNORECASE) for p in patterns)

def send_stock_notification(url, price=None):
    try:
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")
        receiver_emails_env = os.getenv("RECEIVER_EMAIL", "kaka_0814@ymobile.ne.jp,route666@live.cn")
        receiver_emails = [email.strip() for email in receiver_emails_env.split(",")]
        
        if not sender_email or not sender_password:
            print("Warning: Email credentials not configured. Set SENDER_EMAIL and SENDER_PASSWORD environment variables.")
            return False
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ", ".join(receiver_emails)
        msg['Subject'] = "🎉 POPMART Stock Alert - Item Available!"
        
        price_text = f"\nPrice: {price}" if price else ""
        body = f"""
Good news! The item you're watching is now in stock:

URL: {url}{price_text}
Checked at: {jst_now_iso()}

Don't miss out - add it to your cart now!
        """.strip()
        
        msg.attach(MIMEText(body, 'plain'))
        
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
        
        print(f"✅ Stock notification sent to {', '.join(receiver_emails)}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email notification: {e}")
        return False

def check(url: str):
    attempts = int(os.getenv("RETRIES", "3"))
    wait_ms = int(os.getenv("RETRY_WAIT_MS", "1200"))
    last_error = None

    for attempt in range(1, attempts + 1):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
                ctx = browser.new_context(
                    user_agent=os.getenv("USER_AGENT", "Mozilla/5.0 (X11; Linux x86_64) "
                                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                                        "Chrome/124.0.0.0 Safari/537.36"),
                    locale="ja-JP",
                    timezone_id="Asia/Tokyo",
                )
                page = ctx.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_timeout(1500)

                # Cookie banner (best-effort)
                for sel in [
                    'button:has-text("同意")',
                    'button:has-text("同意する")',
                    'button:has-text("同意して閉じる")',
                    'button:has-text("Accept")',
                ]:
                    try:
                        btn = page.locator(sel)
                        if btn.first.is_visible():
                            btn.first.click(timeout=1500)
                            page.wait_for_timeout(300)
                            break
                    except Exception:
                        pass

                page.wait_for_timeout(1200)

                # Collect button-like texts
                merged = []
                for q in ["button", "button, [role='button'], a, .btn, .button"]:
                    try:
                        merged += [t.strip() for t in page.locator(q).all_text_contents() if t.strip()]
                    except Exception:
                        pass
                # de-dupe preserving order
                seen, merged_unique = set(), []
                for t in merged:
                    if t not in seen:
                        seen.add(t); merged_unique.append(t)

                # Price (best-effort)
                price = None
                for sel in ["[class*=price]", ".price", "[data-testid*=price]", "span:has-text('¥')"]:
                    try:
                        for t in page.locator(sel).all_text_contents():
                            if "¥" in t:
                                price = t.strip()
                                break
                        if price: break
                    except Exception:
                        pass

                in_stock_signal = False
                sold_out_signal = False
                disabled_signal = False

                for locator in ["button", "[role='button']", "a", ".btn", ".button", "form button"]:
                    loc = page.locator(locator)
                    count = min(loc.count(), 30)
                    for i in range(count):
                        el = loc.nth(i)
                        try:
                            label = (el.text_content() or "").strip()
                            if text_matches_any(label, ADD_TO_CART_PATTERNS):
                                try:
                                    if el.is_disabled():
                                        disabled_signal = True
                                    else:
                                        in_stock_signal = True
                                except Exception:
                                    in_stock_signal = True
                            if text_matches_any(label, SOLD_OUT_PATTERNS):
                                sold_out_signal = True
                        except Exception:
                            pass

                if not in_stock_signal and any(text_matches_any(t, ADD_TO_CART_PATTERNS) for t in merged_unique):
                    in_stock_signal = True
                if any(text_matches_any(t, SOLD_OUT_PATTERNS) for t in merged_unique):
                    sold_out_signal = True

                if sold_out_signal or disabled_signal:
                    status, in_stock = "OUT_OF_STOCK", False
                elif in_stock_signal:
                    status, in_stock = "IN_STOCK", True
                else:
                    status, in_stock = "UNKNOWN", None

                result = {
                    "url": url,
                    "in_stock": in_stock,
                    "status": status,
                    "detected_texts_sample": merged_unique[:10],
                    "price": price,
                    "checked_at": jst_now_iso(),
                }
                
                # Send email notification if item is in stock
                if in_stock:
                    send_stock_notification(url, price)
                
                browser.close()
                return result

        except Exception as e:
            last_error = str(e)
            if attempt < attempts:
                time.sleep(wait_ms / 1000.0)

    return {
        "url": url, "in_stock": None, "status": "ERROR",
        "error": last_error, "checked_at": jst_now_iso(),
    }

def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.popmart.com/jp/products/3884"
    print(json.dumps(check(url), ensure_ascii=False))

if __name__ == "__main__":
    main()
