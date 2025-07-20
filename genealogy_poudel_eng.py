import json
from genealogy_class import Person

gopal = Person("Gopal", 1940)
# father = Person("Mike", 1970)
# child = Person("Tom", 2000)

ram_bhadra = Person("Ram Bhadra", None)
gopal.add_child(ram_bhadra)

govinda = Person("Govinda", None)
ram_bhadra.add_child(govinda)

prajapati = Person("Prajapati", None)
ram_bhadra.add_child(prajapati)

chamu = Person("Chamu", None)
ram_bhadra.add_child(chamu)

#Level 34
gautam = Person("Gautam", None)
govinda.add_child(gautam)

laxmidhar = Person("Laxmidhar", None)
ramchandra = Person("RamChandra", None)
devhari = Person("DevHari", None)

gautam.add_childs([laxmidhar, ramchandra, devhari])


# Save to file
with open("genealogy_tree.json", "w") as f:
    json.dump(gopal.to_dict(), f, indent=2)

def print_tree(person, level=0):
    print("  " * level + f"{person.name} ({person.birth_year})")
    for child in person.children:
        print_tree(child, level + 1)

print_tree(gopal)