import json

class Person:
    def __init__(self, name, gender="Male", name_nepali=None, birth_year=None, death_year=None, children=None, place=None, comment=None):
        self.name = name
        self.name_nepali = name_nepali
        self.gender = gender
        self.birth_year = birth_year
        self.death_year = death_year
        self.place = place
        self.comment = comment
        self.children = children or []
        self.father = None  # Person object
        self.father_nepali = "" #actual nepali name
        self.grandfather = None  # Person object
        self.grandfather_nepali = "" #actual nepali name

    def add_child(self, child):
        self.children.append(child)
        child.father = self  # ✅ Link child to self as father
        child.father_nepali = child.father.name_nepali
        if self.father:
            child.grandfather = self.father
            child.grandfather_nepali = self.father.name_nepali

    def add_children(self, children):
        for child in children:
            self.add_child(child)

    def to_dict(self, father=None, grandfather=None, father_nepali=None, grandfather_nepali=None):
        return {
            "name": self.name,
            "name_nepali": self.name_nepali,
            "birth_year": self.birth_year,
            "death_year": self.death_year,
            "place": self.place,
            "comment": self.comment,
            "father": father,
            "father_nepali": father_nepali,
            "grandfather": grandfather,
            "grandfather_nepali": grandfather_nepali,
            "children": [
                child.to_dict(father=self.name, grandfather=father, father_nepali=self.name_nepali, grandfather_nepali=self.grandfather_nepali)
                for child in self.children
            ]
        }
