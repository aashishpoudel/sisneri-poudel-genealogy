import re
from genealogy_poudel_data import *
import json
from genealogy_poudel_data import root_person  # or use gopal_31 if that is the root

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

    # Color palette
    colors = ['red', 'green', 'blue', 'orange', 'purple', 'teal', 'brown']
    my_color = colors[level % len(colors)]

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
    Export multiple root trees into ONE HTML and ONE TXT file, in order.

    Example:
        export_roots_trees([gopal_31, bishwamvar_34], print_language="np")

    This will create:
        - sisneri_poudel_tree_np.html
        - sisneri_poudel_tree_np.txt

    where Bishwamvar's full tree follows Gopal's full tree.
    """
    lang = print_language
    if out_html_path is None:
        out_html_path = f"sisneri_poudel_tree_{lang}.html"
    if out_txt_path is None:
        out_txt_path = f"sisneri_poudel_tree_{lang}.txt"

    # ---- HTML prolog (mirrors your export_tree header & styles) ----
    html_lines = [
        '<html><head><meta charset="UTF-8">',
        '<style>',
        'div { font-family: monospace; font-size: 20px; white-space: pre; }',
        'img.icon { height: 1.2em; width: auto; vertical-align: -0.15em; margin-right: 0.35em; }',
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

    text_lines = []

    # ---- For each root, render a section then append the full tree ----
    for idx, root in enumerate(roots):
        # Section heading (per language)
        # root_title = (root.name_nep or root.name) if lang == "np" else (root.name or root.name_nep or "")
        # heading_html = f"<h2 style='margin:10px 0 6px'>{escape(root_title)}</h2>"
        # html_lines.append(heading_html)
        # text_lines.append(root_title)

        # Render this root exactly like export_tree does (re-using your print_tree)
        section_text = []
        section_html = []

        # Build colored/connected HTML prefix segments using your existing print_tree
        print_tree(
            root,
            print_language=lang,
            text_lines=section_text,
            html_lines=section_html,
            level=0
        )

        # Append tree to combined outputs
        html_lines.extend(section_html)
        text_lines.extend(section_text)

        # Divider between sections (except after the last)
        if idx < len(roots) - 1:
            html_lines.append('<hr style="margin:16px 0">')
            text_lines.append("\n" + ("=" * 40) + "\n")

    # ---- Shared popup scripts (same as export_tree) ----
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
        "    if (top + ph + pad > vh) top = r.top - ph - pad;",
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
        '</script>',
        '</body></html>'
    ]

    # ---- Write combined TXT & HTML ----
    with open(out_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(text_lines))

    with open(out_html_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))

    print(f"✅ {out_html_path} and {out_txt_path} generated (order: {', '.join((r.name_nep or r.name) for r in roots)})")
    return out_html_path, out_txt_path

def update_index_html_in_place(index_path="index.html"):
    # Flatten tree with all required fields in one line
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

    genealogy_list = flatten_person(root_person)
    genealogy_json = json.dumps(genealogy_list, ensure_ascii=False, separators=(",", ":"))  # compact, one-line JSON

    # Read the original index.html
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Replace only the genealogyData line
    pattern = r"(const\s+genealogyData\s*=\s*)\[[\s\S]*?\](\s*;)"
    replacement = f"{pattern[0]}{genealogy_json}{pattern[1]}"

    new_html_content = re.sub(pattern, f"\\1{genealogy_json}\\2", html_content)

    # Overwrite the same file
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(new_html_content)

    print("✅ index.html successfully updated with genealogyData.")

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
    # Example combined outputs: Gopal first, then Bishwamvar
    for language in ("en", "np"):
        export_roots_trees(
            roots=[gopal_32, bishwamvar_34],   # order matters
            print_language=language,
            out_html_path=f"sisneri_poudel_tree_{language}.html",
            out_txt_path=f"sisneri_poudel_tree_{language}.txt"
        )

    # Keep your index.html updater as-is
    update_index_html_in_place("index.html")


# Simple Tree
# def print_tree(person, level=0):
#     print("  " * level + f"{person.name} ({person.birth_year})")
#     for child in person.children:
#         print_tree(child, level + 1)

