from genealogy_poudel_data import *

# Save to file
with open("genealogy_tree.json", "w") as f:
    json.dump(gopal_31.to_dict(), f, indent=2)

# Print tree with visual guide indentation
def print_tree(person, prefix="", is_last=True):
    connector = "└── " if is_last else "├── "
    if person.birth_year:
        print(prefix + connector + f"{person.name} ({person.birth_year})")
    else:
        print(prefix + connector + f"{person.name}")

    child_count = len(person.children)
    for i, child in enumerate(person.children):
        is_child_last = (i == child_count - 1)
        new_prefix = prefix + ("    " if is_last else "│   ")
        print_tree(child, new_prefix, is_child_last)

# Simple Tree
# def print_tree(person, level=0):
#     print("  " * level + f"{person.name} ({person.birth_year})")
#     for child in person.children:
#         print_tree(child, level + 1)

print_tree(gopal_31)