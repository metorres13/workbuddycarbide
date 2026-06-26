#!/usr/bin/env python3
"""Fix orphaned B2B card fragments and other cleanup issues"""
import re
from pathlib import Path

ROOT = Path("/Users/nicky/ZCodeProject/carbide-site")

def fix_file(filepath):
    content = filepath.read_text(encoding="utf-8")
    modified = False

    # Fix 1: Remove orphaned b2b-card inner content (without opening aside)
    # Pattern: stray b2b-icon/b2b-body/b2b-btn without opening <aside class="b2b-card">
    orphan = re.search(
        r'<div class="b2b-icon">.*?</div>\s*<div class="b2b-body">.*?</div>\s*<a[^>]*class="b2b-btn"[^>]*>.*?</a>',
        content, re.DOTALL
    )
    if orphan:
        content = content.replace(orphan.group(0), "")
        modified = True

    # Fix 2: Remove any remaining standalone </aside> that lost its opening tag
    if re.search(r'</aside>', content):
        # Check if there's an unmatched </aside>
        open_count = len(re.findall(r'<aside[^>]*>', content))
        close_count = len(re.findall(r'</aside>', content))
        if close_count > open_count:
            # Remove the last unmatched </aside>
            content = re.sub(r'\n</aside>', '', content, count=1)
            modified = True

    # Fix 3: Remove duplicate Tailwind/Config injections
    # Count tailwind CDN
    tw_count = content.count('cdn.tailwindcss.com')
    if tw_count > 1:
        # Keep only first one
        lines = content.split('\n')
        new_lines = []
        seen_tw = False
        for line in lines:
            if 'cdn.tailwindcss.com' in line:
                if not seen_tw:
                    new_lines.append(line)
                    seen_tw = True
            elif 'tailwind.config' in line and seen_tw:
                continue
            elif 'nav-v2-style' in line and seen_tw:
                # Already have nav style
                if 'id="nav-v2-style"' in line:
                    continue
                new_lines.append(line)
            else:
                new_lines.append(line)
        content = '\n'.join(new_lines)
        modified = True

    # Fix 4: Remove duplicate nav-v2-style blocks
    nav_style_count = content.count('id="nav-v2-style"')
    if nav_style_count > 1:
        # Keep only first
        parts = content.split('id="nav-v2-style"')
        first = parts[0] + 'id="nav-v2-style"' + parts[1].split('</style>', 1)[0] + '</style>'
        rest = content[content.index('id="nav-v2-style"', len(first)):]
        # Remove all additional nav-v2-style blocks
        while 'id="nav-v2-style"' in rest:
            idx = rest.index('id="nav-v2-style"')
            end = rest.index('</style>', idx) + len('</style>')
            rest = rest[:idx] + rest[end:]
        content = first + rest
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
        if fix_file(f):
            fixed += 1
    print(f"Fixed {fixed} files")

if __name__ == "__main__":
    main()
