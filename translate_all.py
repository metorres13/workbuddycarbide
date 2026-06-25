#!/usr/bin/env python3
"""
Carbide-Tooling.com — Full Multi-Language Re-translation
Re-translates all non-English pages from English source via Alibaba Cloud MT API.
"""
import os, re, json, sys, time, uuid, hashlib, hmac, base64, urllib.parse
import concurrent.futures
from collections import OrderedDict

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = "/Users/nicky/ZCodeProject/carbide-site"

# ── Credentials ──
# Auto-load credentials from .env file if present
_env_file = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_file):
    with open(_env_file) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                _v = _v.strip().strip('"').strip("'")
                os.environ.setdefault(_k.strip(), _v)

AK = os.environ.get("ALIBABA_AK", "")
SK = os.environ.get("ALIBABA_SK", "")

# ── Language config ──
LANGUAGES = OrderedDict([
    ("de", {"dir": "de", "api": "de", "hreflang": "de", "label": "Deutsch"}),
    ("ja", {"dir": "jp", "api": "ja", "hreflang": "ja", "label": "日本語"}),
    ("es", {"dir": "es", "api": "es", "hreflang": "es", "label": "Español"}),
    ("vi", {"dir": "vi", "api": "vi", "hreflang": "vi", "label": "Tiếng Việt"}),
])

# ── CNC term corrections ──
CNC_TERMS = {
    "de": {"Speed": "Schnittgeschwindigkeit", "Feed": "Vorschub"},
    "ja": {"Speed": "切削速度", "Feed": "送り"},
    "es": {"Speed": "Velocidad de corte", "Feed": "Avance"},
    "vi": {"Speed": "Tốc độ cắt", "Feed": "Lượng chạy dao"},
}

def post_process_html(html_str, lang_key):
    """Apply CNC term corrections after API translation."""
    import re as _re
    terms = CNC_TERMS.get(lang_key, {})
    for en_term, translated_term in sorted(terms.items(), key=lambda x: -len(x[0])):
        html_str = html_str.replace(en_term, translated_term)
    # Fix specific bad general-model translations
    if lang_key == "de":
        html_str = html_str.replace("Schnell- und Vorschub", "Schnittgeschwindigkeit & Vorschub")
        html_str = html_str.replace("Schnell und Vorschub", "Schnittgeschwindigkeit und Vorschub")
    # Fix missing spaces around CNC (API often merges "CNCSpeed" etc.)
    html_str = _re.sub(r'(?<=[a-z0-9])CNC(?=[A-Za-z])', r' CNC', html_str)
    html_str = _re.sub(r'(?<=[a-z0-9])Schnittgeschwindigkeit', r' Schnittgeschwindigkeit', html_str)
    html_str = _re.sub(r'(?<=[a-z0-9])Tốc độ', r' Tốc độ', html_str)
    # Normalize multiple spaces (but not inside pre/code)
    html_str = _re.sub(r'  +', ' ', html_str)
    return html_str

# ── Progress file ──
PROGRESS_FILE = os.path.join(ROOT, ".translation_progress.json")

# ── API caller ──
def percent_encode(s):
    return urllib.parse.quote(s, safe='~')

def translate_text(text, source_lang="en", target_lang="de"):
    """Translate a single text string via Alibaba Cloud MT API."""
    if not text or not text.strip():
        return text
    # Pre-process: ensure space between merged words (API sometimes merges "CNCSpeed")
    text = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', ' ', text)
    
    params = {
        "Action": "TranslateGeneral",
        "FormatType": "text",
        "SourceLanguage": source_lang,
        "TargetLanguage": target_lang,
        "SourceText": text,
        "Scene": "general",  # Could use "domain" for technical CNC content
        "Version": "2018-10-12",
        "Format": "JSON",
        "AccessKeyId": AK,
        "Timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "SignatureMethod": "HMAC-SHA1",
        "SignatureNonce": str(uuid.uuid4()),
        "SignatureVersion": "1.0",
    }
    sorted_keys = sorted(params.keys())
    canonical = "&".join(
        f"{percent_encode(k)}={percent_encode(str(params[k]))}" for k in sorted_keys
    )
    string_to_sign = f"POST&{percent_encode('/')}&{percent_encode(canonical)}"
    signature = base64.b64encode(
        hmac.new(
            (SK + "&").encode("utf-8"),
            string_to_sign.encode("utf-8"),
            hashlib.sha1,
        ).digest()
    ).decode()
    params["Signature"] = signature
    
    for attempt in range(3):
        try:
            r = requests.post("https://mt.aliyuncs.com/", data=params, timeout=30)
            data = r.json()
            if "Data" in data:
                return data["Data"]["Translated"]
            elif "Message" in data:
                print(f"  ⚠ API error: {data['Message']}, retrying...")
                time.sleep(2)
            else:
                print(f"  ⚠ Unexpected response: {json.dumps(data, ensure_ascii=False)[:200]}")
                return text
        except Exception as e:
            print(f"  ⚠ Request failed: {e}, retrying...")
            time.sleep(2)
    print(f"  ✗ Failed after 3 retries, keeping original")
    return text

def translate_batch(texts, source_lang="en", target_lang="de", max_workers=5):
    """Translate multiple texts in parallel."""
    if not texts:
        return {}
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {}
        for idx, txt in enumerate(texts):
            if txt and txt.strip():
                f = executor.submit(translate_text, txt, source_lang, target_lang)
                future_map[f] = idx
            else:
                results[idx] = txt
        for f in concurrent.futures.as_completed(future_map):
            idx = future_map[f]
            try:
                results[idx] = f.result()
            except Exception as e:
                print(f"  ✗ Translation {idx} failed: {e}")
                results[idx] = texts[idx]  # keep original
    return results

# ── Extract translatable text from HTML ──
def extract_texts(html_path):
    """Parse HTML and return (soup, texts_dict) where texts_dict maps unique IDs to (tag_type, location_info, original_text)."""
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    soup = BeautifulSoup(content, "html.parser")
    segments = []
    
    # 1. Title
    title_tag = soup.find("title")
    if title_tag and title_tag.string and title_tag.string.strip():
        segments.append({
            "id": "title", "type": "title",
            "original": title_tag.string.strip(),
            "setter": lambda soup, t: setattr(soup.find("title"), "string", t)
        })
    
    # 2. Meta description
    for meta in soup.find_all("meta"):
        name = meta.get("name", "") or meta.get("property", "")
        if name in ("description", "og:description", "og:title"):
            content_attr = meta.get("content", "")
            if content_attr and content_attr.strip():
                segments.append({
                    "id": f"meta_{name}",
                    "type": "meta",
                    "original": content_attr.strip(),
                    "setter": lambda soup, t, m=meta: m.__setitem__("content", t)
                })
    
    # 3. JSON-LD
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            ld = json.loads(script.string)
            texts_found = []
            
            def extract_ld_texts(obj, path=""):
                if isinstance(obj, str):
                    texts_found.append((path, obj))
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        extract_ld_texts(item, f"{path}[{i}]")
                elif isinstance(obj, dict):
                    for k, v in obj.items():
                        if k in ("name", "description", "headline", "alternateName"):
                            extract_ld_texts(v, f"{path}.{k}")
                        
            extract_ld_texts(ld)
            
            for path, text in texts_found:
                seg_id = f"ld_{id(script)}_{path}"
                segments.append({
                    "id": seg_id,
                    "type": "jsonld",
                    "original": text.strip(),
                    "setter": None,  # Handle JSON-LD separately
                    "ld_path": path,
                    "ld_script": script,
                })
        except:
            pass
    
    # 4. Visible text in HTML body
    text_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "button",
                  "label", "th", "td", "blockquote", "cite", "figcaption", "dt", "dd"]
    
    # Collect specific text elements
    for tag in soup.find_all(text_tags):
        raw = tag.get_text(strip=True)
        if not raw:
            continue
        # Skip if it's just numbers/units
        if re.match(r'^[\d\s.,/+\-%°µ²³]+$', raw):
            continue
        # Check for mixed content (inline tags inside heading)
        inline_tags = ["span", "strong", "em", "b", "i", "code"]
        has_inline = any(isinstance(child, Tag) and child.name in inline_tags for child in tag.children)
        
        if has_inline and tag.name in ("h1", "h2", "h3"):
            # Translate full heading text as one segment, discard inline formatting
            segments.append({
                "id": f"mixed_{id(tag)}",
                "type": "mixed_heading",
                "original": raw,
                "tag": tag,
            })
        else:
            segments.append({
                "id": f"text_{id(tag)}",
                "type": "text",
                "original": raw,
                "setter": None,
                "tag": tag,
            })
    
    # 5. Link text (a tags with text only, not icons/images)
    for tag in soup.find_all("a"):
        raw = tag.get_text(strip=True)
        if not raw or len(raw) < 2:
            continue
        # Skip if it's just a language code (EN, DE, JP, ES, VI, etc.)
        if re.match(r'^[A-Z]{2,4}$', raw):
            continue
        # Skip if it contains an image inside
        if tag.find("img"):
            continue
        segments.append({
            "id": f"link_{id(tag)}",
            "type": "text",
            "original": raw,
            "setter": None,
            "tag": tag,
        })
    
    # 6. Alt attributes on images
    for tag in soup.find_all("img", alt=True):
        alt_text = tag.get("alt", "").strip()
        if alt_text and len(alt_text) > 2:
            segments.append({
                "id": f"alt_{id(tag)}",
                "type": "attr",
                "attr_name": "alt",
                "original": alt_text,
                "setter": lambda soup, t, tg=tag: tg.__setitem__("alt", t)
            })
    
    # 7. Placeholder attributes
    for tag in soup.find_all("input", placeholder=True):
        ph = tag.get("placeholder", "").strip()
        if ph:
            segments.append({
                "id": f"ph_{id(tag)}",
                "type": "attr",
                "attr_name": "placeholder",
                "original": ph,
                "setter": lambda soup, t, tg=tag: tg.__setitem__("placeholder", t)
            })
    
    # 8. Title attributes on elements (not image alt)
    for tag in soup.find_all(attrs={"title": True}):
        if tag.name == "img":
            continue  # Already handled alt
        title_text = tag.get("title", "").strip()
        if title_text:
            segments.append({
                "id": f"title_{id(tag)}",
                "type": "attr",
                "attr_name": "title",
                "original": title_text,
                "setter": lambda soup, t, tg=tag: tg.__setitem__("title", t)
            })
    
    return soup, segments

def apply_translations(soup, segments, translated_texts):
    """Apply translated text back into the HTML soup."""
    for i, seg in enumerate(segments):
        translated = translated_texts.get(i)
        if translated is None or translated == seg["original"]:
            continue
        
        seg_type = seg.get("type")
        
        if seg_type == "title":
            new_string = NavigableString(translated)
            title_tag = soup.find("title")
            if title_tag:
                title_tag.clear()
                title_tag.append(new_string)
        
        elif seg_type == "meta":
            setter = seg.get("setter")
            if setter:
                setter(soup, translated)
        
        elif seg_type == "attr":
            setter = seg.get("setter")
            if setter:
                setter(soup, translated)
        
        elif seg_type == "text":
            tag = seg.get("tag")
            if tag:
                # Replace text content but keep child HTML elements
                for child in list(tag.children):
                    if isinstance(child, NavigableString) and child.strip():
                        if child.strip() == seg["original"]:
                            try:
                                child.replace_with(NavigableString(translated))
                            except:
                                pass
        
        elif seg_type == "mixed_heading":
            tag = seg.get("tag")
            if tag:
                # Replace entire heading content with translated plain text
                tag.clear()
                tag.append(NavigableString(translated))
        
        elif seg_type == "jsonld":
            # Handle JSON-LD by modifying the parsed object
            try:
                ld = json.loads(seg["ld_script"].string)
                parts = seg["ld_path"].lstrip(".").split(".")
                obj = ld
                for part in parts:
                    if "[" in part:
                        arr_name, idx = part.split("[")
                        idx = int(idx.rstrip("]"))
                        obj = obj[arr_name][idx]
                    else:
                        obj = obj[part]
                if isinstance(obj, str):
                    # Navigate back up... too complex, simpler: just str.replace
                    seg["ld_script"].string = seg["ld_script"].string.replace(seg["original"], translated)
            except:
                pass  # Best effort for JSON-LD

def update_hreflang(soup, source_rel_path, lang_key, canonical_host="https://carbide-tooling.com"):
    """
    Update/insert canonical + hreflang alternate links.
    source_rel_path: relative path of the English source (e.g. "tools/speed-feed/")
    lang_key: current page's language key
    """
    for link in soup.find_all("link", rel="alternate"):
        link.decompose()
    for link in soup.find_all("link", rel="canonical"):
        link.decompose()
    
    # Strip trailing index.html for cleaner URLs
    clean_source = re.sub(r'/index\.html$', '/', source_rel_path)
    if clean_source.endswith('/'):
        clean_source = clean_source
    
    # Add canonical for this language
    this_dir = LANGUAGES[lang_key]["dir"]
    canon_path = f"{this_dir}/{clean_source}" if lang_key != "en" else clean_source
    canon_url = f"{canonical_host}/{canon_path}"
    canon_url = re.sub(r'(?<!:)/{2,}', '/', canon_url)
    soup.head.append(soup.new_tag("link", rel="canonical", href=canon_url))
    
    # Add x-default (English version)
    xdefault_url = f"{canonical_host}/{clean_source}"
    xdefault_url = re.sub(r'(?<!:)/{2,}', '/', xdefault_url)
    soup.head.append(soup.new_tag("link", rel="alternate", hreflang="x-default", href=xdefault_url))
    
    # Add hreflang for all languages (including English)
    all_langs = list(LANGUAGES.items()) + [("en", {"dir": "", "hreflang": "en"})]
    for each_lang_key, lang_info in all_langs:
        lang_dir = lang_info["dir"]
        hl = lang_info["hreflang"]
        url_path = f"{lang_dir}/{clean_source}" if lang_dir else clean_source
        url = f"{canonical_host}/{url_path}"
        url = re.sub(r'(?<!:)/{2,}', '/', url)
        soup.head.append(soup.new_tag("link", rel="alternate", hreflang=hl, href=url))

def fix_page_metadata(soup, lang_key):
    """Fix lang attribute, og:locale, and other metadata."""
    # Fix html lang attribute
    html_tag = soup.find("html")
    if html_tag:
        lang_code = LANGUAGES[lang_key]["api"]  # Use API code for lang attr (ja, not jp)
        html_tag["lang"] = lang_code
    
    # Fix og:locale
    for meta in soup.find_all("meta", property="og:locale"):
        locale_map = {"de": "de_DE", "ja": "ja_JP", "es": "es_ES", "vi": "vi_VN"}
        meta["content"] = locale_map.get(lang_key, "en_US")

def get_relative_path(html_path):
    """Get relative path from ROOT."""
    return os.path.relpath(html_path, ROOT)

def get_target_path(source_abs_path, lang_key):
    """Get the target file path for a given language."""
    rel = get_relative_path(source_abs_path)
    lang_dir = LANGUAGES[lang_key]["dir"]
    
    if rel.startswith("tools/"):
        return os.path.join(ROOT, lang_dir, rel)
    elif rel == "index.html":
        return os.path.join(ROOT, lang_dir, "index.html")
    elif rel in ("about.html", "quote.html", "robots.txt"):
        return os.path.join(ROOT, lang_dir, rel)
    elif rel.startswith("guides/"):
        return os.path.join(ROOT, lang_dir, rel)
    else:
        return os.path.join(ROOT, lang_dir, rel)

def get_all_source_pages():
    """Get all English HTML pages that need translation."""
    pages = []
    
    # Tool pages
    tools_dir = os.path.join(ROOT, "tools")
    for tool in sorted(os.listdir(tools_dir)):
        sub = os.path.join(tools_dir, tool)
        if not os.path.isdir(sub):
            continue
        tool_path = os.path.join(sub, "index.html")
        if os.path.isfile(tool_path):
            pages.append(tool_path)
    
    # Root pages
    for page_name in ["index.html", "about.html", "quote.html"]:
        page_path = os.path.join(ROOT, page_name)
        if os.path.isfile(page_path):
            pages.append(page_path)
    
    # Guides
    guides_dir = os.path.join(ROOT, "guides")
    if os.path.isdir(guides_dir):
        for guide_file in sorted(os.listdir(guides_dir)):
            if guide_file.endswith(".html") or guide_file == "index.html":
                pages.append(os.path.join(guides_dir, guide_file))
            else:
                guide_index = os.path.join(guides_dir, guide_file, "index.html")
                if os.path.isfile(guide_index):
                    pages.append(guide_index)
    
    return pages

def load_progress():
    """Load translation progress from file."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"completed": {}, "total_characters": 0}

def save_progress(progress):
    """Save translation progress to file."""
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

def translate_page(html_path, lang_key, progress):
    """Translate a single HTML page to the target language."""
    lang_dir = LANGUAGES[lang_key]["dir"]
    rel_path = get_relative_path(html_path)
    
    # Check if already completed
    completed_key = f"{rel_path}->{lang_key}"
    if completed_key in progress.get("completed", {}):
        print(f"  ✓ Already completed: {completed_key}")
        return 0
    
    target_path = get_target_path(html_path, lang_key)
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    
    # Parse and extract texts from English source
    soup, segments = extract_texts(html_path)
    
    if not segments:
        # No translatable text, copy as-is but with hreflang fixes
        shutil.copy2(html_path, target_path)
        progress.setdefault("completed", {})[completed_key] = True
        return 0
    
    # Translate all segments
    originals = [s["original"] for s in segments]
    
    # Deduplicate identical texts to save API calls
    seen = {}
    dedup_indices = []
    for i, t in enumerate(originals):
        if t in seen:
            dedup_indices.append((i, seen[t]))
        else:
            seen[t] = i
            dedup_indices.append((i, i))
    
    # Translate unique texts only
    unique_indices = sorted(set(idx for _, idx in dedup_indices))
    unique_texts = [originals[idx] for idx in unique_indices]
    
    print(f"  Translating {len(originals)} texts ({len(unique_texts)} unique)...")
    translated_unique = translate_batch(unique_texts, "en", lang_key)
    
    # Map back to all segments
    translated_all = {}
    for orig_idx, unique_idx in dedup_indices:
        if unique_idx in translated_unique:
            translated_all[orig_idx] = translated_unique[unique_idx]
        else:
            translated_all[orig_idx] = originals[orig_idx]
    
    # Apply translations to soup
    apply_translations(soup, segments, translated_all)
    
    # Fix metadata
    fix_page_metadata(soup, lang_key)
    
    # Build relative path for hreflang
    if rel_path == "index.html":
        hreflang_path = f"{lang_dir}/"
    elif rel_path.startswith("tools/"):
        hreflang_path = f"{lang_dir}/{rel_path}"
    else:
        hreflang_path = f"{lang_dir}/{rel_path}"
    
    # Build clean English path for hreflang
    if rel_path == "index.html":
        english_path = ""
    elif rel_path.startswith("tools/"):
        english_path = rel_path
    else:
        english_path = rel_path
    
    update_hreflang(soup, english_path, lang_key)
    
    # Post-process and write
    html_str = post_process_html(str(soup), lang_key)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(html_str)
    
    # Update progress
    char_count = sum(len(t) for t in unique_texts)
    progress.setdefault("completed", {})[completed_key] = True
    progress["total_characters"] = progress.get("total_characters", 0) + char_count
    
    return char_count

def translate_all_single(target_lang=None):
    """Translate all English pages to one specific language."""
    pages = get_all_source_pages()
    print(f"Found {len(pages)} English source pages to translate")
    progress = load_progress()
    total_chars = 0
    
    for lang_key in LANGUAGES:
        if target_lang and lang_key != target_lang:
            continue
        lang_info = LANGUAGES[lang_key]
        print(f"\n{'='*60}")
        print(f"Translating to {lang_info['label']} ({lang_info['api']})")
        print(f"{'='*60}")
        
        for i, page_path in enumerate(pages):
            rel = get_relative_path(page_path)
            print(f"  [{i+1}/{len(pages)}] {rel}")
            chars = translate_page(page_path, lang_key, progress)
            total_chars += chars
            save_progress(progress)
    
    return total_chars

def translate_all():
    """Main translation function."""
    pages = get_all_source_pages()
    print(f"Found {len(pages)} English source pages to translate")
    
    progress = load_progress()
    total_chars = 0
    total_pages = 0
    
    for lang_key in LANGUAGES:
        lang_info = LANGUAGES[lang_key]
        print(f"\n{'='*60}")
        print(f"Translating to {lang_info['label']} ({lang_info['api']})")
        print(f"{'='*60}")
        
        for i, page_path in enumerate(pages):
            rel = get_relative_path(page_path)
            print(f"  [{i+1}/{len(pages)}] {rel}")
            chars = translate_page(page_path, lang_key, progress)
            total_chars += chars
            total_pages += 1
            save_progress(progress)  # Save after each page for resume
    
    print(f"\n{'='*60}")
    print(f"Translation complete!")
    print(f"Total pages translated: {total_pages}")
    print(f"Total characters: {total_chars}")
    print(f"Progress saved to: {PROGRESS_FILE}")

def fix_english_hreflang():
    """Add hreflang tags to English pages that don't have them yet."""
    # Add "en" to LANGUAGES temporarily for hreflang generation
    import copy
    
    def add_en_hreflang(soup, source_rel_path):
        """Like update_hreflang but for English pages."""
        for link in soup.find_all("link", rel="alternate"):
            link.decompose()
        for link in soup.find_all("link", rel="canonical"):
            link.decompose()
        
        clean_source = re.sub(r'/index\.html$', '/', source_rel_path)
        if clean_source.endswith('/'):
            clean_source = clean_source
        
        # Canonical for English
        canon_url = f"https://carbide-tooling.com/{clean_source}"
        canon_url = re.sub(r'(?<!:)/{2,}', '/', canon_url)
        soup.head.append(soup.new_tag("link", rel="canonical", href=canon_url))
        
        # x-default
        xdefault_url = f"https://carbide-tooling.com/{clean_source}"
        xdefault_url = re.sub(r'(?<!:)/{2,}', '/', xdefault_url)
        soup.head.append(soup.new_tag("link", rel="alternate", hreflang="x-default", href=xdefault_url))
        
        # All languages
        for each_lang_key, lang_info in list(LANGUAGES.items()) + [("en", {"dir": "", "hreflang": "en"})]:
            lang_dir = lang_info["dir"]
            hl = lang_info["hreflang"]
            url_path = f"{lang_dir}/{clean_source}" if lang_dir else clean_source
            url = f"https://carbide-tooling.com/{url_path}"
            url = re.sub(r'(?<!:)/{2,}', '/', url)
            soup.head.append(soup.new_tag("link", rel="alternate", hreflang=hl, href=url))
    
    # Root and guide pages
    for root_page in ["index.html", "about.html", "quote.html", "guides/index.html",
                        "guides/carbide-grades.html", "guides/coating-comparison.html",
                        "guides/end-mill-geometry.html", "guides/insert-grade-selection.html",
                        "guides/sourcing-from-china.html"]:
        p = os.path.join(ROOT, root_page)
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
            if soup.find("link", rel="alternate"):
                continue
            rel_path = os.path.relpath(p, ROOT)
            add_en_hreflang(soup, rel_path)
            with open(p, "w", encoding="utf-8") as f:
                f.write(str(soup))
            print(f"  Added hreflang to: {rel_path}")
    
    # Tool pages
    tools_dir = os.path.join(ROOT, "tools")
    for tool in sorted(os.listdir(tools_dir)):
        sub = os.path.join(tools_dir, tool)
        if not os.path.isdir(sub):
            continue
        tp = os.path.join(sub, "index.html")
        if os.path.isfile(tp):
            with open(tp, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
            if soup.find("link", rel="alternate"):
                continue
            rel_path = os.path.relpath(tp, ROOT)
            add_en_hreflang(soup, f"tools/{tool}/")
            with open(tp, "w", encoding="utf-8") as f:
                f.write(str(soup))
            print(f"  Added hreflang to: {rel_path}")

if __name__ == "__main__":
    import shutil
    import glob
    import argparse
    
    parser = argparse.ArgumentParser(description="Translate all pages or fix hreflang")
    parser.add_argument("--fix-hreflang", action="store_true", help="Only fix English hreflang")
    parser.add_argument("--lang", help="Translate only one language (de/ja/es/vi)")
    args = parser.parse_args()
    
    if args.fix_hreflang:
        fix_english_hreflang()
        print("English hreflang fix complete!")
    elif args.lang:
        translate_all_single(args.lang)
    else:
        translate_all()
        fix_english_hreflang()
    import shutil
    translate_all()
