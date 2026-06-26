#!/usr/bin/env python3
"""Final cleanup: remove orphans, old sections, duplicates"""
import re
from pathlib import Path

ROOT = Path("/Users/nicky/ZCodeProject/carbide-site")

def cleanup_file(filepath):
    content = filepath.read_text(encoding="utf-8")
    modified = False

    # 1. Remove standalone </aside> with leading whitespace/surrounding empty lines
    old = content
    # Match a lone </aside> on its own line (with optional whitespace before)
    content = re.sub(r'\n\s*</aside>\s*\n', '\n', content)
    content = re.sub(r'\n\s*</aside>\s*$', '\n', content)
    # Match </aside> that follows only whitespace after another element
    content = re.sub(r'\n\s*\n\s*</aside>', '', content)
    if content != old:
        modified = True

    # 2. Remove remaining old "more-tools" sections (any with hardcoded <section class="more-tools">)
    # These were supposed to be replaced by Global Engineering Directory
    old2 = content
    content = re.sub(
        r'<section class="more-tools">.*?</section>',
        '', content, flags=re.DOTALL
    )
    if content != old2:
        modified = True

    # 3. Remove old lang-switcher sections (the old one that's been replaced by the nav)
    old3 = content
    # Remove standalone lang-switcher divs in footer area 
    content = re.sub(
        r'<div class="lang-switcher"[^>]*>.*?</div>',
        '', content, flags=re.DOTALL
    )
    if content != old3:
        modified = True

    # 4. Remove duplicate hreflang blocks 
    # Count <link...hreflang...> tags
    hreflangs = re.findall(r'<link[^>]*hreflang="[^"]*"[^>]*>', content)
    unique_hrefs = set()
    cleaned_hreflangs = []
    for h in hreflangs:
        # Extract href
        href_match = re.search(r'href="([^"]*)"', h)
        hreflang_match = re.search(r'hreflang="([^"]*)"', h)
        if href_match and hreflang_match:
            key = (hreflang_match.group(1), href_match.group(1))
            if key not in unique_hrefs:
                unique_hrefs.add(key)
                cleaned_hreflangs.append(h)
        else:
            cleaned_hreflangs.append(h)

    if len(cleaned_hreflangs) < len(hreflangs):
        # Need to dedup
        for h in hreflangs:
            content = content.replace(h, '', 1)
        # Insert cleaned hreflangs before </head>
        hreflang_block = '\n'.join(cleaned_hreflangs)
        content = content.replace('</head>', f'\n{hreflang_block}\n</head>', 1)
        modified = True

    # 5. Remove empty lines (3+ consecutive newlines -> 2)
    old5 = content
    content = re.sub(r'\n\n\n+', '\n\n', content)
    if content != old5:
        modified = True

    if modified:
        filepath.write_text(content, encoding="utf-8")
        return True
    return False

def main():
    fixed = 0
    for f in ROOT.rglob("*.html"):
        if ".git" in str(f) or ".venv" in str(f) or "__pycache__" in str(f):
            continue
        if cleanup_file(f):
            fixed += 1
    print(f"Cleaned up {fixed} files")

if __name__ == "__main__":
    main()
