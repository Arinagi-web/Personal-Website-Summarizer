import sys
import os

# Ensure the root directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from browser import fetch_with_browser

def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_html_browser.py <url>", file=sys.stderr)
        sys.exit(1)
        
    url = sys.argv[1]
    try:
        # Reconfigure stdout to use utf-8 encoding on Windows
        sys.stdout.reconfigure(encoding='utf-8')
        html = fetch_with_browser(url)
        print(html)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
