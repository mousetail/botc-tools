from dataclasses import dataclass
import os
import json


@dataclass
class Character:
    name: str
    description: str
    image: str
    script: str
    category: str | None


@dataclass
class ReminderToken:
    character: Character
    name: str
    has_daytime_effect: bool
    drunk_or_poisoned: bool


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
                                    in ("Townsfolk", "Outsider", "Minions", "Demons")
                                ]
                            )
                            and a[0]
                        )
                        or None,
                    )
                )
    character_info.sort(key=lambda i: (i.script, i.category or ""))
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
        for j in i["reminders"]
        if i["name"] in character_name_description_map
    ]

    reminder_tokens.sort(key=lambda i: (i.character.script, i.character.category or ""))
    return [i for i in reminder_tokens if i.name != "No ability"]
