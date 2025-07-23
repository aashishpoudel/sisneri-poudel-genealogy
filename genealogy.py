from genealogy_poudel_data import *

# Save to file
with open("genealogy_tree.json", "w") as f:
    json.dump(gopal_31.to_dict(), f, indent=2)

# Print tree with visual guide indentation
def print_tree(person, prefix="", is_last=True, print_language="en",
               text_lines=None, html_lines=None):
    connector = "└── " if is_last else "├── "
    name = person.nepali_name if print_language == "np" else person.name
    label = f"{name} ({person.birth_year})" if person.birth_year else name
    line = prefix + connector + label

    # Print to console
    print(line)

    # Save to text file list
    if text_lines is not None:
        text_lines.append(line)

    # Save to HTML list
    if html_lines is not None:
        indent = prefix.replace("│", "|").replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;")
        html_lines.append(f"<div>{indent}{connector}{label}</div>")

    # Recursively process children
    child_count = len(person.children)
    for i, child in enumerate(person.children):
        is_child_last = (i == child_count - 1)
        new_prefix = prefix + ("    " if is_last else "│   ")
        print_tree(child, new_prefix, is_child_last, print_language, text_lines, html_lines)


# Example usage:
def export_tree(root_person, print_language="en"):
    text_lines = []
    html_lines = [
        '<html><head><meta charset="UTF-8">',
        '<style>div { font-family: monospace; font-size: 16px; }</style>',
        '</head><body>'
    ]

    print_tree(root_person, print_language=print_language,
               text_lines=text_lines, html_lines=html_lines)

    html_lines.append('</body></html>')

    # Write text output
    with open("family_tree_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(text_lines))

    # Write HTML output
    with open("family_tree_output.html", "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))


# Example:
export_tree(gopal_31, print_language="np")  # Make sure you have a Person instance assigned to `root_person`


# Simple Tree
# def print_tree(person, level=0):
#     print("  " * level + f"{person.name} ({person.birth_year})")
#     for child in person.children:
#         print_tree(child, level + 1)

print_tree(gopal_31, print_language="np")