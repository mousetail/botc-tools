from dataclasses import dataclass
import os
import json
import functools
from typing import Protocol


class Token(Protocol):
    def get_number_of_instances(self) -> int:
        pass


@dataclass
@functools.total_ordering
class Character:
    name: str
    description: str
    image: str
    script: str
    category: str | None

    def get_sort_key(self):
        script_order = {
            "trouble brewing": 0,
            "bad moon rising": 1,
            "sects and violets": 2,
            "bad moon rising": 3,
            "travellers": 4,
            "fabled": 5,
            "experimental": 6,
        }
        category_order = {"Townsfolk": 0, "Outsiders": 1, "Minions": 2, "Demons": 3}
        return (
            script_order[self.script],
            category_order[self.category] if self.category else 4,
            self.name,
        )

    def __lt__(self, other):
        return self.get_sort_key() < other.get_sort_key()

    def get_number_of_instances(self):
        if self.name == "Legion":
            return 7
        elif self.name == "Riot":
            return 3
        
        if self.name == "Imp":
            return 3
        else:
            return 1


@dataclass
@functools.total_ordering
class ReminderToken:
    character: Character
    name: str
    has_daytime_effect: bool
    drunk_or_poisoned: bool

    def get_sort_key(self):
        return (self.character.get_sort_key(), self.name)

    def __lt__(self, other):
        return self.get_sort_key() < other.get_sort_key()

    def get_number_of_instances(self):
        if self.name == "No ability":
            return 0
        if self.character.category == "Demons" and self.name == "Dead":
            return 0
        if self.character.name == "Noble" and self.name == "Seen":
            return 3
        if self.character.name == "Tea Lady" and self.name == "Can not die":
            return 2
        if self.character.name == "Preacher" and self.name == "At\u00a0a sermon":
            return 3
        if self.character.name == "Mathematician":
            return 4
        if self.character.name == "Juggler":
            return 5
        if self.character.name == "Barber":
            return 2

        if self.name == "Visitor":
            return 2
        if self.name == "Chose death":
            return 3
        if self.name == "Chose life":
            return 3
        else:
            return 1


def get_character_tokens(characters_folder: str) -> list[Character]:
    character_info: list[Character] = []

    # Read each character's JSON file and generate Character objects
    for filename in os.listdir(characters_folder):
        if filename.endswith(".json"):
            with open(os.path.join(characters_folder, filename), "r") as json_file:
                character = json.load(json_file)
                character_info.append(
                    Character(
                        name=character["name"],
                        description=character["description"],
                        image=character["image"],
                        script=character["script"],
                        category=(
                            (
                                a := [
                                    i
                                    for i in character["groups"]
                                    if i
                                    in ("Townsfolk", "Outsiders", "Minions", "Demons")
                                ]
                            )
                            and a[0]
                        )
                        or None,
                    )
                )
    character_info.sort()
    return character_info


def get_reminder_tokens(character_info: list[Character]) -> list[ReminderToken]:
    character_name_description_map = {i.name: i for i in character_info}

    with open("characters.json") as f:
        reminder_tokens_info = json.load(f)

    reminder_tokens = [
        ReminderToken(
            character=character_name_description_map[i["name"]],
            name=j,
            has_daytime_effect=(
                "day" in character_name_description_map[i["name"]].description
                or "execute" in character_name_description_map[i["name"]].description
                or "any time" in character_name_description_map[i["name"]].description
            ),
            drunk_or_poisoned=j in ("Drunk", "Poisoned"),
        )
        for i in reminder_tokens_info
        for j in i["reminders"] + i.get("remindersGlobal", [])
        if i["name"] in character_name_description_map
    ]

    reminder_tokens.sort()
    return reminder_tokens


def expand_iterable(tokens: list[Token]) -> list[Token]:
    expanded_list = []

    for token in tokens:
        for i in range(token.get_number_of_instances()):
            yield token

    return expanded_list
