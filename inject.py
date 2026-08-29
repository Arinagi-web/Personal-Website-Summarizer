import re
from pathlib import Path

def main():
    WEBSITE_ROOT = Path("LadyIrwin")
    SCRIPT_FILENAME = "summarizer.js"
    CHATBOT_FILENAME = "chatbot.js"
    
    html_files = list(WEBSITE_ROOT.rglob("*.html"))
    total_files = len(html_files)
    summarizer_injected_count = 0
    chatbot_injected_count = 0
    already_done_count = 0
    failed_count = 0
    
    for html_file in html_files:
        try:
            # Calculate depth relative to WEBSITE_ROOT
            rel_path = html_file.relative_to(WEBSITE_ROOT)
            depth = len(rel_path.parts) - 1
            
            # Build correct script path
            if depth == 0:
                script_src = SCRIPT_FILENAME
                chatbot_src = CHATBOT_FILENAME
            else:
                script_src = "../" * depth + SCRIPT_FILENAME
                chatbot_src = "../" * depth + CHATBOT_FILENAME
                
            script_tag = f'<script src="{script_src}"></script>'
            chatbot_tag = f'<script src="{chatbot_src}"></script>'
            
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            already_has_summarizer = SCRIPT_FILENAME in content
            already_has_chatbot = CHATBOT_FILENAME in content

            if already_has_summarizer and already_has_chatbot:
                print(f"⚠ Already injected: {html_file}")
                already_done_count += 1
                continue
                
            # Inject before </body> (case-insensitive)
            if re.search(r'</body>', content, re.IGNORECASE):
                # Inject whatever is missing
                tags_to_inject = ""
                if not already_has_summarizer:
                    tags_to_inject += f'{script_tag}\n'
                    summarizer_injected_count += 1
                if not already_has_chatbot:
                    tags_to_inject += f'{chatbot_tag}\n'
                    chatbot_injected_count += 1

                new_content = re.sub(
                    r'(</body>)', 
                    f'{tags_to_inject}\\1', 
                    content, 
                    flags=re.IGNORECASE,
                    count=1
                )
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✓ Injected: {html_file}")
            else:
                print(f"✗ Failed (no </body> found): {html_file}")
                failed_count += 1
                
        except Exception as e:
            print(f"✗ Failed error on {html_file}: {e}")
            failed_count += 1

    print(f"\nDone: {summarizer_injected_count} files injected with summarizer, {chatbot_injected_count} files injected with chatbot, {already_done_count} already done, {failed_count} failed")

if __name__ == "__main__":
    main()
