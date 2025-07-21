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
