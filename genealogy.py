import re
from genealogy_poudel_data import *
import json
from genealogy_poudel_data import root_person  # or use gopal_31 if that is the root

GENERATION_COLORS = ['red', 'green', 'blue', 'orange', 'purple', 'teal', 'brown', '#C71585', 'navy', 'darkmagenta']

# Save to file
genealogy_json_file = "genealogy_tree.json"
with open(genealogy_json_file, "w") as f:
    json.dump(gopal_32.to_dict(), f, indent=2)
    print(f"✅ {genealogy_json_file} successfully updated with genealogyData.")

# Print tree with visual guide indentation
def print_tree(person, level=0, prefix="", is_last=True, print_language="en",
               text_lines=None, html_lines=None, parent_color=None,
               vertical_color_map=None):
    """
    Recursively build the genealogy tree as HTML.

    This function walks the `Person` hierarchy starting from the given node,
    and produces an indented, styled HTML representation of the family tree.
    It includes icons for gender, plus signs for newly added persons, and
    asterisks with tooltips for comments.

    :param person: The current Person node to render.
    :param prefix: String prefix used for indentation and connector lines.
    :param is_last: True if this person is the last child of the parent, controls connector rendering.
    :param lang: Language code for rendering the name ("en" or "np").
    :param my_color: Hex color string for styling connectors for this generation.
    :param generation: Current generation depth, used for color-coding.
    :return: List of HTML lines representing this person and all descendants.
    """
    if text_lines is None:
        text_lines = []
    if html_lines is None:
        html_lines = []
    if vertical_color_map is None:
        vertical_color_map = {}

    my_color = GENERATION_COLORS[level % len(GENERATION_COLORS)]

    # Connector characters (skip for root level)
    if level == 0:
        connector = ""  # no connector for root
    else:
        connector = "└── " if is_last else "├── "

    # --- TEXT OUTPUT ---
    text_line = prefix + connector + person.name
    text_lines.append(text_line)

    # --- HTML OUTPUT (prefix with colored verticals) ---
    html_prefix = ""
    col_idx = 0  # Track which column in monospace the char is in
    for char in prefix:
        if char in ['│', '├', '└', '─']:
            color = vertical_color_map.get(col_idx, parent_color or my_color)
            html_prefix += f'<span style="color:{color}">{char}</span>'
        else:
            html_prefix += char
        col_idx += 1

    # Add connector and name
    connector_html = ''.join(f'<span style="color:{parent_color or my_color}">{c}</span>' for c in connector)

    # Display name (EN/NP) + optional place/year
    name = person.name if print_language == "en" else person.name_nep
    print_words = name or ""
    if person.place:
        print_words += f"({person.place})"
    if person.birth_year:
        # add birth year inside the last open paren if present; else open new
        if "(" in print_words and not print_words.endswith(")"):
            print_words += f"{person.birth_year})"
        else:
            print_words += f"({person.birth_year})"

    # Parent / grandparent data attributes
    father = person.father
    grandfather = person.grandfather
    father_name = father.name if father else ""
    grandfather_name = grandfather.name if grandfather else ""

    # Font-size: Nepali slightly bigger
    font_size = 24 if print_language == "en" else 28

    # Base label HTML
    name_html = (
        f'<span style="color:{my_color}; font-size:{font_size}px" '
        f'data-name="{person.name}" data-father="{father_name}" data-grandfather="{grandfather_name}">'
        f'{print_words}</span>'
    )

    # Optional female icon
    icon_src = "images/girl_icon_new2.png"
    icon_html = ""
    if getattr(person, "gender", "") == "Female":
        icon_html = f'<img src="{icon_src}" class="icon" alt="Girl Icon">'

    # Optional "addition" plus sign
    plus_html = ""
    if getattr(person, "addition", False):
        plus_html = ' <span style="color:{0}; font-weight:bold">+</span>'.format(my_color)

    # --- Comment asterisk (popup trigger) ---
    def _escape_attr(s: str) -> str:
        # Basic HTML attr escape + newline to &#10; so JS getAttribute() yields real newlines
        return (s.replace("&", "&amp;")
                 .replace("<", "&lt;")
                 .replace(">", "&gt;")
                 .replace('"', "&quot;")
                 .replace("\r\n", "\n")
                 .replace("\n", "&#10;"))

    comment_text = getattr(person, "comment", "") or ""
    if comment_text.strip():
        esc = _escape_attr(comment_text)
        # Make the asterisk adopt the generation color
        name_html += (
            f' <a href="#" class="cm" style="color:{my_color}" title="View note" '
            f'   data-cmt="{esc}">*</a>'
        )

    # Append this line
    html_lines.append(f"<div>{html_prefix}{connector_html}{icon_html}{name_html}{plus_html}</div>")

    # Prepare for children
    new_prefix = prefix + ("    " if is_last else "│   ")
    if not is_last:
        vertical_color_map[col_idx] = parent_color or my_color  # Extend vertical line with same color
    elif col_idx in vertical_color_map:
        del vertical_color_map[col_idx]  # Remove if no more verticals needed

    child_count = len(person.children)
    for i, child in enumerate(person.children):
        print_tree(child,
                   level=level + 1,
                   prefix=new_prefix,
                   is_last=(i == child_count - 1),
                   print_language=print_language,
                   text_lines=text_lines,
                   html_lines=html_lines,
                   parent_color=my_color,
                   vertical_color_map=vertical_color_map.copy())



# Example usage:
def export_tree(root_person, print_language="en"):
    """
    Export the complete genealogy tree to an HTML file.

    Calls `print_tree` starting from the root ancestor, wraps the output in a
    full HTML document template (with CSS), and writes it to a language-specific file.

    :param root: The root Person object (earliest known ancestor).
    :type root: Person
    :param lang: Language code for rendering ("en" for English, "np" for Nepali).
    :type lang: str
    :return: Path of the generated HTML file.
    :rtype: str
    """
    text_lines = []
    html_lines = [
        '<html><head><meta charset="UTF-8">',
        '<style>',
        # Your existing base styles:
        'div { font-family: monospace; font-size: 29px; white-space: pre; }',
        'img.icon { height: 1.2em; width: auto; vertical-align: -0.15em; margin-right: 0.35em; }',

        # NEW: asterisk and popup styles
        'a.cm { text-decoration: none; font-weight: bold; margin-left: 0.25rem; cursor: pointer; }',
        'a.cm:focus { outline: 2px solid #999; outline-offset: 2px; }',
        '#comment-popup { position: fixed; z-index: 9999; display: none; display: inline-flex; align-items: center; width: auto; max-width: 70vw; padding: 8px 10px; '
            'background: #fff; border: 1px solid #ccc; box-shadow: 0 6px 18px rgba(0,0,0,.15); '
            'border-radius: 8px; font-size: 14px; line-height: 1.35; white-space: pre-wrap;}',
        '#comment-popup .cp-body { display: inline;}',
        '#comment-popup .cp-close { display: inline-block; margin-left: 10px; background: transparent; border: none; font-size: 16px; cursor: pointer; line-height: 1; }',
        '</style>',
        '</head><body>'
    ]

    print_tree(root_person, print_language=print_language,
               text_lines=text_lines, html_lines=html_lines, level=0)

    # Shared popup element + JS (added before closing body)
    html_lines += [
        '<div id="comment-popup" role="dialog" aria-modal="true" aria-label="Note">',
        '  <div class="cp-body"></div>',
        '  <button class="cp-close" aria-label="Close">×</button>',
        '</div>',
        '<script>',
        '(function(){',
        '  const popup = document.getElementById("comment-popup");',
        '  const body = popup.querySelector(".cp-body");',
        '  const closeBtn = popup.querySelector(".cp-close");',
        '  let openFrom = null;',
        '  function closePopup(){ popup.style.display="none"; openFrom=null; }',
        '  function openPopup(anchor, text){',
        '    body.textContent = text || "";',
        '    popup.style.display = "block";',
        '    const r = anchor.getBoundingClientRect();',
        '    const pad = 8;',
        '    let top = r.bottom + pad, left = r.left;',
        '    const vw = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);',
        '    const vh = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);',
        '    const pw = popup.offsetWidth, ph = popup.offsetHeight;',
        '    if (left + pw + pad > vw) left = vw - pw - pad;',
        '    if (top + ph + pad > vh) top = r.top - ph - pad;',
        '    if (top < pad) top = pad;',
        '    if (left < pad) left = pad;',
        '    popup.style.top = Math.round(top) + "px";',
        '    popup.style.left = Math.round(left) + "px";',
        '    openFrom = anchor;',
        '  }',
        '  document.addEventListener("click", function(e){',
        '    const a = e.target.closest("a.cm");',
        '    if (a){',
        '      e.preventDefault();',
        '      const txt = a.getAttribute("data-cmt") || "";',
        '      // getAttribute returns real newlines from &#10;',
        '      if (popup.style.display==="block" && openFrom===a) { closePopup(); }',
        '      else { openPopup(a, txt); }',
        '      e.stopPropagation();',
        '      return;',
        '    }',
        '    if (popup.style.display==="block" && !e.target.closest("#comment-popup")) closePopup();',
        '  }, true);',
        '  closeBtn.addEventListener("click", function(e){ e.preventDefault(); closePopup(); });',
        '  ["scroll","keydown","resize"].forEach(evt => window.addEventListener(evt, closePopup, {passive:true}));',
        '  document.addEventListener("visibilitychange", function(){ if (document.hidden) closePopup(); });',
        '  document.addEventListener("input", closePopup, true);',
        '})();',
        '</script>'
    ]

    html_lines.append('</body></html>')

    # Write text output
    with open(f"sisneri_poudel_tree_{print_language}.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(text_lines))

    # Write HTML output
    html_file = f"sisneri_poudel_tree_{print_language}.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))

    print(f"✅ {html_file} - Tree exported for {'english' if print_language=='en' else 'nepali'}.")

from html import escape
import re

def _strip_tags(html: str) -> str:
    """Minimal HTML tag stripper for plain-text export."""
    return re.sub(r"<[^>]+>", "", html)

def export_roots_trees(roots, print_language="en",
                       out_html_path=None, out_txt_path=None):
    """
    Export multiple root trees into ONE HTML and ONE TXT file, with a fixed
    generation banner aligned to the vertical lines.
    """
    START_GEN = 32

    # ---- compute END_GEN across all roots ----
    def max_depth(p):
        if not getattr(p, "children", None):
            return 0
        return 1 + max(max_depth(c) for c in p.children)

    deepest = 0
    for rt in roots:
        d = max_depth(rt)
        if d > deepest:
            deepest = d
    END_GEN = START_GEN + deepest  # inclusive

    # ---- colors block (cycle palette) ----
    palette = list(GENERATION_COLORS)
    color_rules = [f".tick.c{g} {{ color: {palette[(g - START_GEN) % len(palette)]}; }}"
                   for g in range(START_GEN, END_GEN + 1)]

    lang = print_language
    if out_html_path is None:
        out_html_path = f"sisneri_poudel_tree_{lang}.html"
    if out_txt_path is None:
        out_txt_path = f"sisneri_poudel_tree_{lang}.txt"

    # ---- HTML prolog (with banner CSS) ----
    html_lines = [
        '<html><head><meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',  # Already present, but confirm syntax
        # Optional: Import a consistent monospace font with Devanagari support (add this line)
        '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Mono&family=Noto+Sans+Devanagari&display=swap" rel="stylesheet">',
        '<style>',
        # Updated font-family for better consistency (use imported fonts if possible)
        'div { font-family: "Noto Sans Mono", "Noto Sans Devanagari", monospace; font-size: 29px; white-space: pre; }',
        'img.icon { height: 1.2em; width: auto; vertical-align: -0.15em; margin-right: 0.35em; }',
        'a.cm { text-decoration: none; font-weight: bold; margin-left: 0.25rem; cursor: pointer; }',
        'a.cm:focus { outline: 2px solid #999; outline-offset: 2px; }',
        '#comment-popup { position: fixed; z-index: 9999; display: none; inline-flex; align-items: center; width: auto; max-width: 70vw; padding: 8px 10px; '
        'background: #fff; border: 1px solid #ccc; box-shadow: 0 6px 18px rgba(0,0,0,.15); '
        'border-radius: 8px; font-size: 14px; line-height: 1.35; white-space: pre-wrap;}',
        # Fixed typo: removed duplicate 'display: none;'
        '#comment-popup .cp-body { display: inline;}',
        '#comment-popup .cp-close { display: inline-block; margin-left: 10px; background: transparent; border: none; font-size: 16px; cursor: pointer; line-height: 1; }',
        '#generationBanner{ position:fixed; top:0; left:0; right:0; height:var(--gen-banner-h); background:#fff; border-bottom:1px solid #e5e5e5; z-index:2000; }',
        '#genRuler{ position:relative; height:100%; font-family:monospace; font-size:1.5em; line-height:var(--gen-banner-h); }',
        '.tick{ position:absolute; top:0; transform:translateX(-50%); font-weight:800; user-select:none; pointer-events:none; }',
        *color_rules,
        # ADD: Media query for mobile (reduces squeezing by making text smaller)
        '@media (max-width: 768px) {',
        '  div { font-size: 20px; }',  # Smaller base font
        '  span { font-size: inherit !important; }',  # Override inline font sizes
        '  #genRuler { font-size: 1.2em; }',  # Slightly smaller banner text
        '}',
        '</style>',
        '</head><body>',
        '<div id="generationBanner"><div id="genRuler"></div></div>'
    ]

    text_lines = []

    # ---- Render each root ----
    for idx, root in enumerate(roots):
        section_text = []
        section_html = []
        print_tree(
            root,
            print_language=lang,
            text_lines=section_text,
            html_lines=section_html,
            level=0
        )
        html_lines.extend(section_html)
        text_lines.extend(section_text)

        if idx < len(roots) - 1:
            html_lines.append('<hr style="margin:16px 0">')
            text_lines.append("\n" + ("=" * 40) + "\n")

    # ---- shared popup & banner JS ----
    # ---- shared popup & banner JS ----
    # ---- shared popup & banner JS ----
    # ---- shared popup & banner JS ----
    html_lines += [
        '<script>',
        '(function(){',
        f'  const START_GEN = {START_GEN}, END_GEN = {END_GEN};',
        f'  const IS_NEPALI = {"true" if print_language == "np" else "false"};',
        '  const ruler = document.getElementById("genRuler");',
        '  function toNep(str){ const m={"0":"०","1":"१","2":"२","3":"३","4":"४","5":"५","6":"६","7":"७","8":"८","9":"९"}; return str.replace(/\\d/g,d=>m[d]); }',
        '  function getRootSpan(){ return document.querySelector(\'span[data-name]\'); }',
        '  function getVerticalColumns(rootX){',
        '    const spans = Array.from(document.querySelectorAll("span"));',
        '    const xs = [];',
        '    for (const s of spans){',
        '      if (s.textContent==="│"){',
        '        const rect = s.getBoundingClientRect();',
        '        xs.push(Math.round(rect.left));',
        '      }',
        '    }',
        '    xs.sort((a,b)=>a-b);',
        '    const uniq=[]; for (const x of xs){ if (x>rootX+4 && (uniq.length===0 || Math.abs(x-uniq[uniq.length-1])>2)) uniq.push(x); }',
        '    return uniq;',
        '  }',
        '  function render(){',
        '    const root = getRootSpan(); if (!root) return;',
        '    const rb = root.getBoundingClientRect();',
        '    const rootX = Math.round(rb.left);',
        '    const cols = getVerticalColumns(rootX);',
        '    ruler.innerHTML = "";',
        '    let step;',
        '    if (cols.length >= 2) {',
        '      const deltas = [];',
        '      for (let i = 1; i < cols.length; i++) deltas.push(cols[i] - cols[i - 1]);',
        '      const avg = deltas.reduce((a,b)=>a+b,0) / deltas.length;',
        '      const firstGap = cols[0] - rootX;',
        '      step = (avg + firstGap) / 2;',
        '    } else if (cols.length === 1) {',
        '      step = cols[0] - rootX;',
        '    } else {',
        '      step = 48;',
        '    }',
        '    if (!isFinite(step) || step < 8) step = 48;',
        '    const label = document.createElement("div");',
        '    label.className = "tick";',
        '    label.style.left = "0px";',
        '    label.textContent = IS_NEPALI ? "    पुस्ता" : "   Gen";',
        '    ruler.appendChild(label);',
        '    for (let g = START_GEN; g <= END_GEN; g++) {',
        '      const t = document.createElement("div");',
        '      t.className = "tick c" + g;',
        '      const lbl = String(g);',
        '      t.textContent = IS_NEPALI ? toNep(lbl) : lbl;',
        '      const x = rootX + 8 + (g - START_GEN + 1) * step;',
        '      t.style.left = x + "px";',
        '      ruler.appendChild(t);',
        '    }',
        '  }',
        '  let renderTimeout;',
        '  function debouncedRender() {',
        '    clearTimeout(renderTimeout);',
        '    renderTimeout = setTimeout(render, 50);',  # 50ms debounce for smooth performance
        '  }',
        '  window.addEventListener("load", debouncedRender);',
        '  window.addEventListener("resize", debouncedRender, {passive:true});',
        '  window.addEventListener("scroll", debouncedRender, {passive:true});',
        # Critical addition for horizontal scroll
        '})();',
        '</script>',
        '</body></html>'
    ]

    with open(out_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(text_lines))
    with open(out_html_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))

    print(f"✅ {out_html_path} and {out_txt_path} generated (order: {', '.join(r.name for r in roots) if print_language=='en' else ', '.join(r.name_nep for r in roots)})")
    return out_html_path, out_txt_path


def update_index_html_in_place(roots, index_path="index.html"):
    """
    Inject per-root arrays and a merged array into index.html:
      const genealogyData_<label> = [...];

    Also writes a merged legacy:
      const genealogyData = [...genealogyData_<label1>, ...genealogyData_<label2>, ...];

    Formatting:
      - One blank line between each const (including before the merged one)
      - One tab ('\t') indent inside the <script> block
      - Removes any prior genealogyData* const blocks before inserting
    """
    import json, re, unicodedata

    # ---- helper: flatten one root tree like your existing code ----
    def flatten_person(person):
        people = [{
            "name": person.name,
            "name_nep": person.name_nep,
            "birth_year": person.birth_year,
            "father": person.father.name if person.father else None,
            "grandfather": person.father.father.name if person.father and person.father.father else None,
            "ggfather": (
                person.father.father.father.name
                if person.father and person.father.father and person.father.father.father
                else None
            ),
            "father_nep": person.father.name_nep if person.father else None,
            "grandfather_nep": person.father.father.name_nep if person.father and person.father.father else None,
            "ggfather_nep": (
                person.father.father.father.name_nep
                if person.father and person.father.father and person.father.father.father
                else None
            ),
        }]
        for child in person.children:
            people.extend(flatten_person(child))
        return people

    # ---- helper: label for variable names (or accept explicit labels) ----
    def slug_from_person(p):
        base = p.name or p.name_nep or "root"
        norm = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode("ascii")
        norm = norm.lower()
        norm = re.sub(r"[^a-z0-9]+", "_", norm).strip("_")
        return norm or "root"

    # normalize roots => list[(label, person)]
    pairs = []
    for item in roots:
        if isinstance(item, tuple) and len(item) == 2:
            label, person = item
        else:
            # derive label from the Python variable name in globals()
            person = item
            for varname, obj in globals().items():
                if obj is person:
                    label = varname
                    break
            else:
                # fallback if not found in globals
                label = slug_from_person(person)

        # sanitize & de-dupe
        label = re.sub(r"[^a-zA-Z0-9_]", "_", label)
        if re.match(r"^[0-9]", label):
            label = f"r_{label}"
        original, n = label, 2
        while any(lbl == label for lbl, _ in pairs):
            label = f"{original}_{n}"
            n += 1
        pairs.append((label, person))

    # build const strings (one per root) + merged
    per_root_consts = []
    merged_spreads = []
    for label, person in pairs:
        plist = flatten_person(person)
        genealogy_json = json.dumps(plist, ensure_ascii=False, separators=(",", ":"))
        per_root_consts.append(f"const genealogyData_{label} = {genealogy_json};")
        merged_spreads.append(f"...genealogyData_{label}")

    merged_const = f"const genealogyData = [{', '.join(merged_spreads)}];"

    # read index.html
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1) remove ANY existing genealogyData* arrays first (single or multiple)
    #    pattern: const genealogyData or const genealogyData_<label> = [ ... ];
    rm_pattern = r"""(?mx)
        ^[ \t]*const[ \t]+genealogyData(?:_[A-Za-z0-9_]+)?[ \t]*=[ \t]*\[[\s\S]*?\][ \t]*;[ \t]*$
    """
    html = re.sub(rm_pattern, "", html)

    # 2) find the first <script ...> to inject after it; capture its leading indent
    m = re.search(r"^([ \t]*)<script\b[^>]*>", html, flags=re.MULTILINE)
    if m:
        script_indent = m.group(1)
        inner_indent = script_indent + "\t"  # one tab deeper than <script>
        block = "\n\n".join(inner_indent + s for s in per_root_consts + [merged_const]) + "\n"
        # insert right after the opening <script> tag
        insert_pos = m.end()
        html = html[:insert_pos] + "\n" + block + html[insert_pos:]
    else:
        # fallback: before </body> (indented with one tab)
        inner_indent = "\t"
        block = "\n\n".join(inner_indent + s for s in per_root_consts + [merged_const]) + "\n"
        html = re.sub(r"</body>", block + "</body>", html, count=1, flags=re.IGNORECASE) or (html + "\n" + block)

    # 3) compact extra blank lines introduced by deletions (optional tidy)
    html = re.sub(r"\n{3,}", "\n\n", html)

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ index.html updated with genealogyData blocks.")

###Todo take below thing out if no issue seen after Aug 15
# # Build parent mapping: child -> parent
# parent_map = {}
#
# def build_parent_map(person, parent=None):
#     for child in person.children:
#         parent_map[child] = person
#         build_parent_map(child, child)
#
# build_parent_map(root_person)

# for language in ("en", "np"):
#     print_tree(gopal_32, print_language=language)
#     export_tree(gopal_32, print_language=language)  # Make sure you have a Person instance assigned to `root_person`

# update_index_html_in_place("index.html")

if __name__ == "__main__":
    # roots is all the root Person of the unconnected family tree
    roots = [gopal_32, bishwamvar_34]
    for language in ("en", "np"):
        export_roots_trees(
            roots,   # order matters
            print_language=language,
            out_html_path=f"sisneri_poudel_tree_{language}.html",
            out_txt_path=f"sisneri_poudel_tree_{language}.txt"
        )

    update_index_html_in_place(roots, index_path="index.html")



# Simple Tree
# def print_tree(person, level=0):
#     print("  " * level + f"{person.name} ({person.birth_year})")
#     for child in person.children:
#         print_tree(child, level + 1)

