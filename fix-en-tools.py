#!/usr/bin/env python3
"""Re-add B2B cards and engineering directories to English tool pages"""
import re, random
from pathlib import Path

ROOT = Path("/Users/nicky/ZCodeProject/carbide-site")

def get_all_tools():
    tools_dir = ROOT / "tools"
    return sorted([d.name for d in tools_dir.iterdir() if d.is_dir() and not d.name.startswith(".")])

def build_directory(tool_name, all_tools):
    available = [t for t in all_tools if t != tool_name]
    selected = random.sample(available, min(10, len(available)))
    random.shuffle(selected)
    
    def display(t):
        return t.replace("-", " ").title()
    
    links = "".join(f'<a href="/tools/{t}/">{display(t)}</a>\n' for t in selected)
    
    return f'''<section class="engineering-directory" style="margin:40px 0 20px;padding:28px 24px;background:linear-gradient(135deg,#f8f9fa 0%,#f5f5f7 100%);border-radius:20px;border:1px solid #e8e8ed">
<h3 style="font-size:16px;font-weight:700;color:#1d1d1f;margin-bottom:6px;text-align:center">🌐 Global Engineering Directory</h3>
<p style="font-size:12px;color:#86868b;text-align:center;margin-bottom:16px">Explore more professional machining tools from our global collection</p>
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:8px">
{links}</div>
</section>
<style>.engineering-directory a{{display:block;font-size:12px;font-weight:500;color:#1d1d1f;text-decoration:none;padding:8px 14px;background:#fff;border-radius:10px;border:1px solid #e8e8ed;transition:all .15s;text-align:center}}.engineering-directory a:hover{{background:#0066cc;color:#fff;border-color:#0066cc;transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,102,204,.15)}}</style>'''

def build_b2b(tool_name):
    display = tool_name.replace("-", " ").title()
    return f'''<aside class="b2b-card-enhanced" style="margin:32px 0">
<div style="display:flex;align-items:center;gap:20px;background:linear-gradient(135deg,#f0f7ff 0%,#e8f4ff 100%);border:1px solid #b8d4f0;border-radius:20px;padding:24px 28px;box-shadow:0 2px 12px rgba(0,102,204,.06)">
<div style="flex-shrink:0;width:52px;height:52px;background:#0066cc;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:24px;box-shadow:0 4px 12px rgba(0,102,204,.2)">📦</div>
<div style="flex:1;min-width:0">
<h3 style="font-size:15px;font-weight:700;color:#1d1d1f;margin:0 0 4px">Professional Solutions for {display}?</h3>
<p style="font-size:12px;color:#555;line-height:1.5;margin:0">Get factory-direct pricing on premium carbide tooling with ISO-certified quality and responsive engineering support.</p>
</div>
<a href="/quote.html" style="flex-shrink:0;display:inline-flex;align-items:center;background:#0066cc;color:#fff;padding:10px 22px;border-radius:24px;font-size:12px;font-weight:600;text-decoration:none;transition:all .2s;white-space:nowrap" onmouseover="this.style.background='#0055aa';this.style.transform='translateY(-1px)';this.style.boxShadow='0 4px 16px rgba(0,102,204,.3)'" onmouseout="this.style.background='#0066cc';this.style.transform='none';this.style.boxShadow='none'">Request Bulk Quote →</a>
</div>
</aside>'''

def fix_file(filepath, all_tools):
    content = filepath.read_text(encoding="utf-8")
    modified = False
    tool_name = filepath.parent.name

    # 1. Remove any old/broken b2b-card fragments
    # Remove orphan <aside class="b2b-card"> (without matching </aside>)
    content = re.sub(r'<aside class="b2b-card"[^>]*>\s*', '', content)
    # Remove any remaining </aside> that's now unmatched (keep valid ones)
    # Actually just clean all old b2b-card class elements
    content = re.sub(r'<aside class="b2b-card"[^>]*>.*?</aside>', '', content, flags=re.DOTALL)

    # 2. Add engineering directory before </body> if not present
    if 'engineering-directory' not in content:
        directory = build_directory(tool_name, all_tools)
        content = content.replace('</body>', f'{directory}\n</body>', 1)
        modified = True

    # 3. Add enhanced B2B card before engineering directory (or before </body>)
    if 'b2b-card-enhanced' not in content:
        b2b = build_b2b(tool_name)
        if 'engineering-directory' in content:
            content = content.replace(
                '<section class="engineering-directory"',
                f'{b2b}\n<section class="engineering-directory"',
                1
            )
        else:
            content = content.replace('</body>', f'{b2b}\n</body>', 1)
        modified = True

    # 4. Clean up triple+ newlines
    content = re.sub(r'\n\n\n+', '\n\n', content)

    if modified:
        filepath.write_text(content, encoding="utf-8")
        return True
    return False

def main():
    all_tools = get_all_tools()
    fixed = 0
    tools_dir = ROOT / "tools"
    for d in tools_dir.iterdir():
        if d.is_dir() and not d.name.startswith("."):
            idx = d / "index.html"
            if idx.exists():
                if fix_file(idx, all_tools):
                    fixed += 1
    print(f"Fixed {fixed} English tool pages")

if __name__ == "__main__":
    main()
