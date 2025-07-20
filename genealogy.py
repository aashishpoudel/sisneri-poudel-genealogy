from genealogy_poudel_data import *

# Save to file
with open("genealogy_tree.json", "w") as f:
    json.dump(gopal_31.to_dict(), f, indent=2)

def print_tree(person, level=0):
    print("  " * level + f"{person.name} ({person.birth_year})")
    for child in person.children:
        print_tree(child, level + 1)

print_tree(gopal_31)