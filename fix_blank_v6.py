"""
Fix V6: Remove hero-img-wrapper + hero-atmo divs from non-English tool pages
These appear BEFORE the nav and create ~500px of blank space at the top.
"""
import os, re, glob

ROOT = '/Users/nicky/ZCodeProject/carbide-site'

fixed = 0
for lang in ['de', 'jp', 'es', 'vi']:
    tool_dir = os.path.join(ROOT, lang, 'tools', '*', 'index.html')
    for fp in sorted(glob.glob(tool_dir)):
        with open(fp, 'r') as f:
            html = f.read()

        original = html

        # 1) Remove hero-img-wrapper block (multi-line, from <div class="hero-img-wrapper"> to its closing </div>)
        # Match: <div class="hero-img-wrapper">\n<img ...> ... </div>
        html = re.sub(
            r'\n<div class="hero-img-wrapper">[\s\S]*?</div>\n',
            '\n',
            html
        )

        # 2) Remove hero-atmo div
        html = re.sub(
            r'\n<div class="hero-atmo" aria-hidden="true"></div>',
            '',
            html
        )

        # 3) Clean up double blank lines (max 2 consecutive)
        html = re.sub(r'\n{3,}', '\n\n', html)

        if html != original:
            with open(fp, 'w') as f:
                f.write(html)
            fixed += 1

print(f"Fixed {fixed} non-English tool pages")
