from playwright.sync_api import sync_playwright
import sys

html_path = r"C:\Users\thadd\.openclaw\workspace\whale_watch_report.html"
pdf_path = r"C:\Users\thadd\OneDrive\Desktop\Spocks Reports\whale_watch\2026-05-13_whale_watch.pdf"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"file:///{html_path}")
    page.pdf(
        path=pdf_path,
        format="A4",
        margin={"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"},
        print_background=True
    )
    browser.close()

print(f"PDF generated: {pdf_path}")