import re
from genealogy_poudel_data import *
import json
from genealogy_poudel_data import root_person  # or use gopal_31 if that is the root

# Save to file
with open("genealogy_tree.json", "w") as f:
    json.dump(gopal_31.to_dict(), f, indent=2)

# Print tree with visual guide indentation
def print_tree(person, level=0, prefix="", is_last=True, print_language="en",
               text_lines=None, html_lines=None, parent_color=None,
               vertical_color_map=None):
    if text_lines is None:
        text_lines = []
    if html_lines is None:
        html_lines = []
    if vertical_color_map is None:
        vertical_color_map = {}

    # Color palette
    colors = ['red', 'green', 'blue', 'orange', 'purple', 'teal', 'brown']
    my_color = colors[level % len(colors)]

    # Connector characters
    connector = "└── " if is_last else "├── "

    # --- TEXT OUTPUT ---
    text_line = prefix + connector + person.name
    text_lines.append(text_line)

    # --- HTML OUTPUT ---
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
    name = person.name if print_language=="en" else person.name_nepali
    print_words = name
    if person.place:
        print_words += f"({person.place})"
    if person.birth_year:
        print_words.replace(")", "")
        print_words += f"({person.birth_year}" if not "(" in print_words else f"{person.birth_year}"
        print_words += ")"

    ###Todo take below thing out if no issue seen after Aug 15
    # Get parent and grandparent info if Person class supports it
    # father = person.father.name if person.father else ""
    # grandfather = person.father.father.name if person.father and person.father.father else ""
    # father = parent_map.get(person)
    # grandfather = parent_map.get(father) if father else None

    father = person.father
    grandfather = person.grandfather

    father_name = father.name if father else ""
    grandfather_name = grandfather.name if grandfather else ""

    name_html = (
        f'<span style="color:{my_color}; font-size: 19px" '
        f'data-name="{person.name}" data-father="{father_name}" data-grandfather="{grandfather_name}">'
        f'{print_words}</span>'
    )
    html_lines.append(f"<div>{html_prefix}{connector_html}{name_html}</div>")

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
                   vertical_color_map=vertical_color_map.copy())  # Important: pass a *copy* per branch


# Example usage:
def export_tree(root_person, print_language="en"):
    text_lines = []
    html_lines = [
        '<html><head><meta charset="UTF-8">',
        '<style>div { font-family: monospace; font-size: 16px; white-space: pre; }</style>',
        '</head><body>'
    ]

    print_tree(root_person, print_language=print_language,
               text_lines=text_lines, html_lines=html_lines, level=0)

    html_lines.append('</body></html>')

    # Write text output
    with open(f"sisneri_poudel_tree_{print_language}.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(text_lines))

    # Write HTML output
    html_file = f"sisneri_poudel_tree_{print_language}.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))

    print(f"✅ {html_file} - Tree exported for {'english' if print_language=='en' else 'nepali'}.")

def update_index_html_in_place(index_path="index.html"):
    # Flatten tree with all required fields in one line
    def flatten_person(person):
        people = [{
            "name": person.name,
            "name_nepali": person.name_nepali,
            "birth_year": person.birth_year,
            "father": person.father.name if person.father else None,
            "grandfather": person.father.father.name if person.father and person.father.father else None,
            "father_nepali": person.father.name_nepali if person.father else None,
            "grandfather_nepali": person.father.father.name_nepali if person.father and person.father.father else None,
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

for language in ("en", "np"):
    print_tree(gopal_31, print_language=language)
    export_tree(gopal_31, print_language=language)  # Make sure you have a Person instance assigned to `root_person`

update_index_html_in_place("index.html")

# Simple Tree
# def print_tree(person, level=0):
#     print("  " * level + f"{person.name} ({person.birth_year})")
#     for child in person.children:
#         print_tree(child, level + 1)

