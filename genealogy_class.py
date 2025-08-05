import json

class Person:
    def __init__(self, name, nepali_name=None, birth_year=None, death_year=None, children=None, place=None, comment=None):
        self.name = name
        self.nepali_name = nepali_name
        self.birth_year = birth_year
        self.death_year = death_year
        self.place = place
        self.comment = comment
        self.children = children or []
        self.father = None  # ✅ Add this
        self.grandfather = None  # Optional, but useful for quick access

    def add_child(self, child):
        self.children.append(child)
        child.father = self  # ✅ Link child to self as father
        if self.father:
            child.grandfather = self.father

    def add_children(self, children):
        for child in children:
            self.add_child(child)

    def to_dict(self, father=None, grandfather=None):
        return {
            "name": self.name,
            "nepali_name": self.nepali_name,
            "birth_year": self.birth_year,
            "death_year": self.death_year,
            "place": self.place,
            "comment": self.comment,
            "father": father,
            "grandfather": grandfather,
            "children": [
                child.to_dict(father=self.name, grandfather=father)
                for child in self.children
            ]
        }
