from genealogy_poudel_data import *
import json, re

GENERATION_COLORS = ['red', 'green', 'blue', 'orange', 'purple', 'teal', 'brown', '#C71585', 'navy', 'darkmagenta']

genealogy_json_file = "genealogy_tree.json"
with open(genealogy_json_file, "w") as f:
    json.dump(gopal_32.to_dict(), f, indent=2)
    print(f"✅ {genealogy_json_file} successfully updated with genealogyData.")

# Print tree with visual guide indentation
def print_tree(person, level=0, prefix="", is_last=True, print_language="en",
               text_lines=None, html_lines=None, parent_color=None,
               vertical_color_map=None, earliest_gen_number=None, color_offset=0):
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



    # --- Root indent offset based on earliest_gen_number ---
    indent_color_offset = 0
    if level == 0 and earliest_gen_number is not None:
        def _root_gen(p):
            gen = getattr(p, "gen_number", None)
            if isinstance(gen, int) and 1 <= gen <= 100:
                return gen
            # fallback: try to recover the variable name and parse digits
            var_name = None
            for var, obj in globals().items():
                if obj is p:
                    var_name = var
                    break
            if var_name:
                m = re.search(r'_(\d+)', var_name)
                if m:
                    return int(m.group(1))
            # last resort: treat as earliest
            return earliest_gen_number

        root_gen = _root_gen(person)
        root_offset = max(0, root_gen - earliest_gen_number)
        color_offset += root_offset
        if root_offset:
            # 4 spaces per level to match existing tree spacing
            prefix += "    " * root_offset

    # Color palette
    my_color = GENERATION_COLORS[(level + color_offset) % len(GENERATION_COLORS)]

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

    # --- Comment asterisk (popup trigger) ---
    def _escape_attr(s: str) -> str:
        # Basic HTML attr escape + newline to &#10; so JS getAttribute() yields real newlines
        return (s.replace("&", "&amp;")
                 .replace("<", "&lt;")
                 .replace(">", "&gt;")
                 .replace('"', "&quot;")
                 .replace("\r\n", "\n")
                 .replace("\n", "&#10;"))

    # Optional "edit" plus sign
    plus_html = correction_html = ""
    if getattr(person, "edit", False) and len(person.edit):
        edit = person.edit
        if edit.strip().startswith("+"):
            plus_comment = edit.strip().replace("+","").strip()
            if plus_comment:
                esc = _escape_attr(plus_comment)
                plus_html += (
                    f' <a href="#" class="cm" style="color:{my_color}" title="View note" '
                    f'   data-cmt="{esc}">+</a>'
                )
            else:
                plus_html += ' <span style="color:{0}; font-weight:bold">+</span>'.format(my_color)
        elif edit.strip().startswith("#"):
            correction_comment = edit.strip().replace("#", "").strip()
            if correction_comment:
                esc = _escape_attr(correction_comment)
                correction_html += (
                    f' <a href="#" class="cm" style="color:{my_color}" title="View note" '
                    f'   data-cmt="{esc}">#</a>'
                )
            else:
                correction_html += ' <span style="color:{0}; font-weight:bold">#</span>'.format(my_color)

    comment_text = getattr(person, "comment", "") or ""
    if comment_text.strip():
        esc = _escape_attr(comment_text)
        # Make the asterisk adopt the generation color
        name_html += (
            f' <a href="#" class="cm" style="color:{my_color}" title="View note" '
            f'   data-cmt="{esc}">*</a>'
        )

    # Append this line
    html_lines.append(f"<div>{html_prefix}{connector_html}{icon_html}{name_html}{plus_html}{correction_html}</div>")

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
                   vertical_color_map=vertical_color_map.copy(),
                   earliest_gen_number=earliest_gen_number,
                   color_offset=color_offset)

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

    def get_var_name(obj, namespace=None):
        if namespace is None:
            namespace = globals()
        return [name for name, val in namespace.items() if val is obj]

    def get_earliest_generation(roots):
        """
        Given a list of Person objects, determine the earliest (minimum) generation number.
        - If gen_number exists and is an integer between 1 and 100, use it.
        - Otherwise, extract from the variable name (e.g., gopal_32 -> 32, hari_33_1 -> 33).

        Args:
            roots (list): list of Person objects

        Returns:
            int: the minimum generation number found
        """
        gen_numbers = []

        for person in roots:
            gen_num = getattr(person, "gen_number", None)
            if isinstance(gen_num, int) and 1 <= gen_num <= 100:
                gen_numbers.append(gen_num)
            else:
                # Fallback: extract digits after first underscore from variable name
                var_name = get_var_name(person)[0]
                if var_name is None:
                    raise ValueError(f"No gen_number and no variable name for {person}")

                match = re.search(r'_(\d+)', var_name)
                if match:
                    gen_numbers.append(int(match.group(1)))
                else:
                    raise ValueError(f"Could not determine generation number for {var_name}")

        return min(gen_numbers) if gen_numbers else None

    earliest_gen_number = get_earliest_generation(roots)

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
            level=0,
            earliest_gen_number=earliest_gen_number
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

    NEW:
      - Each person dict includes "gen_number", derived from the root's generation
        (parsed from the root variable name, e.g., gopal_32 → 32; children increment by depth).
    """
    import json, re, unicodedata

    # ---------- helpers ----------
    def slug_from_person(p):
        base = p.name or p.name_nep or "root"
        norm = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode("ascii")
        norm = re.sub(r"[^a-z0-9]+", "_", norm.lower()).strip("_")
        return norm or "root"

    def extract_root_gen(label, person):
        """
        Pick the root generation from the variable name.
        Examples:
          'gopal_32'      -> 32
          'gopal_32_1'    -> 32   (first plausible 2+ digit number)
          'bishwamvar_34' -> 34
        Fallbacks: person.gen_number, else 32.
        """
        nums = [int(n) for n in re.findall(r'(\d+)', label)]
        for n in nums:
            if n >= 20:  # plausible generation window
                return n
        # fallback to object’s gen_number, then default
        if getattr(person, "gen_number", None):
            return int(person.gen_number)
        return 32

    def flatten_person(person, cur_gen):
        """
        Return a flat list of dicts for this subtree, tagging each with gen_number=cur_gen.
        Also preserves father/grandfather (en/nep) like your existing payload.
        """
        entry = {
            "name": person.name,
            "name_nep": person.name_nep,
            "birth_year": person.birth_year,
            "gen_number": cur_gen,  # <-- NEW
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
        }
        people = [entry]
        for child in person.children:
            people.extend(flatten_person(child, cur_gen + 1))
        return people

    # ---------- normalize roots => list[(label, person, root_gen)] ----------
    pairs = []
    for item in roots:
        if isinstance(item, tuple) and len(item) == 2:
            label, person = item
        else:
            person = item
            # try to recover the python variable name as label
            label = None
            for varname, obj in globals().items():
                if obj is person:
                    label = varname
                    break
            if not label:
                label = slug_from_person(person)

        label = re.sub(r"[^A-Za-z0-9_]", "_", label)
        if re.match(r"^[0-9]", label):
            label = "r_" + label
        # de-dup labels if repeated
        base, i = label, 2
        while any(lbl == label for (lbl, _, __) in pairs):
            label = f"{base}_{i}"
            i += 1

        root_gen = extract_root_gen(label, person)
        pairs.append((label, person, root_gen))

    # ---------- build const strings (per root) + merged ----------
    per_root_consts = []
    merged_spreads = []

    all_gen_ranges = []
    for label, person, root_gen in pairs:
        plist = flatten_person(person, root_gen)
        gen_numbers = [person.get('gen_number') for person in plist if isinstance(person.get('gen_number'), int) and 1 <= person.get('gen_number') <= 100]
        gen_range_tuple = (min(gen_numbers), max(gen_numbers))
        all_gen_ranges.append(gen_range_tuple)
        genealogy_json = json.dumps(plist, ensure_ascii=False, separators=(",", ":"))
        per_root_consts.append(f"const genealogyData_{label} = {genealogy_json};")
        merged_spreads.append(f"...genealogyData_{label}")

    # Calculate total generation number range
    total_gen_range = (min(r[0] for r in all_gen_ranges), max(r[1] for r in all_gen_ranges))
    merged_const = f"const genealogyData = [{', '.join(merged_spreads)}];"

    # ---------- read/patch index.html ----------
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # remove prior genealogyData const blocks (single or multiple)
    rm_pattern = r"""(?mx)
        ^[ \t]*const[ \t]+genealogyData(?:_[A-Za-z0-9_]+)?[ \t]*=[ \t]*\[[\s\S]*?\][ \t]*;[ \t]*$
    """
    html = re.sub(rm_pattern, "", html)

    # insert new consts just after the first <script>, else before </body>
    m = re.search(r"^([ \t]*)<script\b[^>]*>", html, flags=re.MULTILINE)
    if m:
        script_indent = m.group(1)
        inner_indent = script_indent + "\t"
        block = "\n\n".join(inner_indent + s for s in per_root_consts + [merged_const]) + "\n"
        html = html[:m.end()] + "\n" + block + html[m.end():]
    else:
        inner_indent = "\t"
        block = "\n\n".join(inner_indent + s for s in per_root_consts + [merged_const]) + "\n"
        html = re.sub(r"</body>", block + "</body>", html, count=1, flags=re.IGNORECASE) or (html + "\n" + block)

    # tidy and write
    html = re.sub(r"\n{3,}", "\n\n", html)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ index.html updated with genealogyData blocks.")

    # ---------- Replace gen-banner with encircled numbers ----------
    if total_gen_range:
        start, end = total_gen_range

        # Build the circle badges
        circles = []
        for i in range(start, end + 1):
            circles.append(
                f'<span class="gen-dot" aria-label="Generation {i}">{i}</span>'
            )
        numbers_html = "\n      ".join(circles)

        banner_html = (
            '<div id="gen-banner" style="border: 2px solid black; padding: 10px; text-align: center;">\n'
            '    <div class="gen-wrap">\n'
            f'      {numbers_html} <strong class="gen-label">⬅ पुस्ता</strong>\n'
            '    </div>\n'
            '</div>'
        )

        with open(index_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Replace the whole <div id="gen-banner">...</div> block (single-pass)
        new_html = re.sub(
            r'<div id="gen-banner"[^>]*>[\s\S]*?<div class="gen-wrap">[\s\S]*?</div>[\s\S]*?</div>',
            banner_html,
            html_content,
            flags=re.DOTALL
        )

        with open(index_path, "w", encoding="utf-8") as f:
            f.write(new_html)

        print(f"✅ gen-banner updated in {index_path} with encircled generations {start}–{end}")


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

