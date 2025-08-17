import json

class Person:
    def __init__(self, name, gender="Male", name_nep=None, birth_year=None, death_year=None, children=None, place=None, comment=None):
        self.name = name
        self.name_nep = name_nep
        self.gender = gender
        self.birth_year = birth_year
        self.death_year = death_year
        self.place = place
        self.comment = comment
        self.children = children or []
        self.father = None  # Person object
        self.father_nep = "" #actual nepali name
        self.grandfather = None  # Person object
        self.grandfather_nep = "" #actual nepali name

    def add_child(self, child):
        self.children.append(child)
        child.father = self  # ✅ Link child to self as father
        child.father_nep = child.father.name_nep
        if self.father:
            child.grandfather = self.father
            child.grandfather_nep = self.father.name_nep

    def add_children(self, children):
        for child in children:
            self.add_child(child)

    def to_dict(self, father=None, grandfather=None, father_nep=None, grandfather_nep=None):
        return {
            "name": self.name,
            "name_nep": self.name_nep,
            "birth_year": self.birth_year,
            "death_year": self.death_year,
            "place": self.place,
            "comment": self.comment,
            "father": father,
            "father_nep": father_nep,
            "grandfather": grandfather,
            "grandfather_nep": grandfather_nep,
            "children": [
                child.to_dict(father=self.name, grandfather=father, father_nep=self.name_nep, grandfather_nep=self.grandfather_nep)
                for child in self.children
            ]
        }
