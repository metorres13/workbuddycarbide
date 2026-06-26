#!/usr/bin/env python3
"""carbide-tooling.com: SEO关键词注入 + meta优化"""
import re
from pathlib import Path

BASE = Path(__file__).parent
SITE = "https://carbide-tooling.com"

# 所有目标关键词
KEYWORDS = [
    "carbide end mills china", "solid carbide end mill manufacturer", 
    "carbide cutting tools supplier", "carbide inserts for steel turning",
    "cnc cutting tools factory china", "wholesale carbide end mills",
    "carbide tools from china direct", "carbide drill bits factory",
    "turning inserts manufacturer china", "pvd coated carbide inserts",
    "tool holders bt40 supplier", "carbide end mill oem china",
    "cutting tools supplier jiangsu", "custom carbide tools oem",
    "carbide end mill price china", "tungsten carbide tools supplier",
    "indexable carbide inserts china", "cnc tooling direct from factory",
    "solid carbide drills supplier", "carbide threading tools china",
    "boring tools manufacturer china", "carbide reamers supplier",
    "carbide end mill for hardened steel", "carbide milling inserts",
    "carbide tool factory changzhou", "oem carbide cutting tools",
    "carbide inserts for stainless steel", "cnc cutting tools price",
    "carbide end mill coating alTin", "china carbide tool manufacturer iso",
    "micro carbide end mills", "carbide slot drills",
    "carbide burrs supplier", "carbide saw tips china",
    "solid carbide rod supplier", "carbide strip tungsten",
    "diamond cutting tools china", "cnc tool holder hsK",
    "end mill adapter supplier", "face milling cutter china"
]

# 每页的目标关键词
PAGE_KW = {
    "index.html": ["carbide cutting tools supplier", "carbide tools from china direct", "cnc cutting tools factory china", "cutting tools supplier jiangsu"],
    "products/index.html": ["carbide end mills china", "carbide inserts for steel turning", "cnc tooling direct from factory", "wholesale carbide end mills"],
    "products/end-mills.html": ["solid carbide end mill manufacturer", "carbide end mill price china", "carbide end mill coating alTin", "micro carbide end mills"],
    "products/turning-inserts.html": ["turning inserts manufacturer china", "indexable carbide inserts china", "carbide inserts for stainless steel", "pvd coated carbide inserts"],
    "products/drills.html": ["carbide drill bits factory", "solid carbide drills supplier", "carbide tools from china"],
    "products/tool-holders.html": ["tool holders bt40 supplier", "cnc tool holder hsK", "end mill adapter supplier"],
    "products/boring-tools.html": ["boring tools manufacturer china", "carbide reamers supplier", "face milling cutter china"],
    "products/threading-tools.html": ["carbide threading tools china", "carbide end mill oem china"],
    "guides/index.html": ["best carbide end mill for steel", "custom carbide tools oem", "carbide end mill price china"],
    "guides/end-mill-geometry.html": ["solid carbide end mill manufacturer", "carbide end mill coating alTin", "carbide milling inserts"],
    "guides/carbide-grades.html": ["carbide tool factory changzhou", "tungsten carbide tools supplier", "china carbide tool manufacturer iso"],
    "guides/coating-comparison.html": ["pvd coated carbide inserts", "carbide end mill coating alTin"],
    "guides/sourcing-from-china.html": ["carbide cutting tools supplier", "carbide tools from china direct", "cnc cutting tools factory china", "oem carbide cutting tools"],
    "about.html": ["cutting tools supplier jiangsu", "carbide tools from china"],
    "quote.html": ["cnc cutting tools price", "carbide end mill price china", "wholesale carbide end mills"],
}

# 1. 每页加隐藏关键词区
for fpath in BASE.rglob("*.html"):
    if "node_modules" in str(fpath): continue
    c = fpath.read_text(encoding="utf-8")
    orig = c
    
    # 隐藏关键词区
    if "<!-- SEO-KEYWORDS -->" not in c:
        kw_html = '\n<!-- SEO-KEYWORDS -->\n<div style="display:none;">\n'
        fname = fpath.relative_to(BASE).as_posix()
        page_kws = PAGE_KW.get(fname, [])
        # 用全局关键词补充
        all_kws = set(page_kws + KEYWORDS[:10])
        for kw in all_kws:
            kw_html += f"<p>{kw}</p>\n"
        kw_html += '</div>\n<!-- END SEO-KEYWORDS -->\n'
        c = c.replace("</body>", kw_html + "</body>")
    
    # 2. meta description 用关键词优化
    fname = fpath.relative_to(BASE).as_posix()
    page_kws = PAGE_KW.get(fname, [])
    if page_kws and '<meta name="description"' not in c:
        primary_kw = page_kws[0]
        desc = f"Source {primary_kw} directly from China. ISO 9001 certified factory. Competitive pricing, fast delivery, quality assured."
        meta = f'<meta name="description" content="{desc}">\n'
        c = c.replace("</head>", f"{meta}</head>")
    
    if c != orig:
        fpath.write_text(c, encoding="utf-8")
        print(f"✅ {fpath.name}")

print("\n=== 关键词注入完成 ===")
print(f"总关键词数: {len(set(KEYWORDS + sum(PAGE_KW.values(), [])))}")
