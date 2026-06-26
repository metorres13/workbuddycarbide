#!/usr/bin/env python3
"""Targeted fix for zh pages: localized engineering directory + B2B cards"""
import re
from pathlib import Path

ROOT = Path("/Users/nicky/ZCodeProject/carbide-site")

ZH_DIR_TITLE = '🌐 全球工程目录'
ZH_DIR_SUBTITLE = '浏览我们全球系列中的更多专业加工工具'
ZH_B2B_TITLE_PREFIX = '的专业解决方案'
ZH_B2B_BODY = '获取ISO认证品质的优质硬质合金刀具工厂直供价格，以及专业的技术支持。'
ZH_B2B_BTN = '批量询价 →'

def fix_zh_file(filepath):
    content = filepath.read_text(encoding="utf-8")
    modified = False

    # Fix engineering directory title
    old_dir_title = 'Global Engineering Directory'
    if old_dir_title in content:
        content = content.replace(
            f'<h3 style="font-size:16px;font-weight:700;color:#1d1d1f;margin-bottom:6px;text-align:center">🌐 {old_dir_title}</h3>',
            f'<h3 style="font-size:16px;font-weight:700;color:#1d1d1f;margin-bottom:6px;text-align:center">{ZH_DIR_TITLE}</h3>'
        )
        modified = True

    # Fix directory subtitle
    old_dir_sub = 'Explore more professional machining tools from our global collection'
    if old_dir_sub in content:
        content = content.replace(old_dir_sub, ZH_DIR_SUBTITLE)
        modified = True

    # Fix B2B card title - find "Professional Solutions for" in zh pages and replace
    tool_name = filepath.parent.name
    display_name = tool_name.replace("-", " ").title()

    b2b_enhanced = re.search(r'<aside class="b2b-card-enhanced".*?</aside>', content, re.DOTALL)
    if b2b_enhanced:
        old_card = b2b_enhanced.group(0)
        if 'Professional Solutions for' in old_card:
            new_title = f'{display_name}{ZH_B2B_TITLE_PREFIX}'
            new_card = old_card.replace(
                re.search(r'<h3[^>]*>.*?</h3>', old_card).group(0),
                f'<h3 style="font-size:15px;font-weight:700;color:#1d1d1f;margin:0 0 4px">{new_title}</h3>'
            )
            if 'Get factory-direct pricing' in new_card:
                new_card = new_card.replace(
                    re.search(r'<p[^>]*>Get factory-direct pricing.*?</p>', new_card).group(0),
                    f'<p style="font-size:12px;color:#555;line-height:1.5;margin:0">{ZH_B2B_BODY}</p>'
                )
            if 'Request Bulk Quote' in new_card:
                btn_match = re.search(r'>Request Bulk Quote[^<]*<', new_card)
                if btn_match:
                    new_card = new_card.replace(btn_match.group(0), f'>{ZH_B2B_BTN}<')
            if new_card != old_card:
                content = content.replace(old_card, new_card, 1)
                modified = True

    if modified:
        filepath.write_text(content, encoding="utf-8")
        return True
    return False

def main():
    fixed = 0
    zh_tools = ROOT / "zh" / "tools"
    if zh_tools.exists():
        for d in zh_tools.iterdir():
            if d.is_dir() and not d.name.startswith("."):
                idx = d / "index.html"
                if idx.exists():
                    if fix_zh_file(idx):
                        fixed += 1
    print(f"Fixed {fixed} Chinese tool pages")

if __name__ == "__main__":
    main()
