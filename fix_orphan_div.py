"""Fix orphaned </div> after <body> in non-English tool pages."""
import os, re, glob

ROOT = '/Users/nicky/ZCodeProject/carbide-site'

fixed = 0
for lang in ['de', 'jp', 'es', 'vi']:
    tool_dir = os.path.join(ROOT, lang, 'tools', '*', 'index.html')
    for fp in sorted(glob.glob(tool_dir)):
        with open(fp, 'r') as f:
            html = f.read()

        original = html
        
        # Fix: <body>\n</div><nav ... → <body>\n<nav ...
        html = re.sub(r'(<body>\s*)</div>\s*', r'\1', html)
        
        # Clean extra blank lines after <body>
        html = re.sub(r'(<body>)\n{2,}', r'\1\n', html)

        if html != original:
            with open(fp, 'w') as f:
                f.write(html)
            fixed += 1

print(f"Fixed {fixed} orphaned </div> tags")
