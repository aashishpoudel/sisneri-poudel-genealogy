import json

class Person:
    def __init__(self, name, birth_year, children=None):
        self.name = name
        self.birth_year = birth_year
        self.children = children or []

    def add_child(self, child):
        self.children.append(child)

    def add_childs(self, childs):
        for child in childs:
            self.children.append(child)

    def to_dict(self):
        return {
            "name": self.name,
            "birth_year": self.birth_year,
            "children": [child.to_dict() for child in self.children]
        }

    @classmethod
    def from_dict(cls, data):
        name = data["name"]
        birth_year = data["birth_year"]
        children = [cls.from_dict(child) for child in data.get("children", [])]
        return cls(name, birth_year, children)

    def __repr__(self):
        return f"Person({self.name}, {self.birth_year}, {len(self.children)} children)"

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
chamu.add_child(chamu)

# Save to file
with open("genealogy_tree.json", "w") as f:
    json.dump(gopal.to_dict(), f, indent=2)

def print_tree(person, level=0):
    print("  " * level + f"{person.name} ({person.birth_year})")
    for child in person.children:
        print_tree(child, level + 1)

print_tree(gopal)