import os
import json
import re
import functools
import math
from dataclasses import dataclass

from svg_tools import generate_reminder_tokens, generate_character_svg
from constants import *

# Define the path to the characters folder
characters_folder = "characters"


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


def get_page_start_html():
    return f'''
        <svg width="{a4_width}" height="{a4_height}" viewBox="0 0 {a4_width / scale} {a4_height / scale}" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <clipPath id="circleClip">
                    <circle cx="{circle_radius}" cy="{circle_radius}" r="{circle_radius}" />
                </clipPath>
            </defs>
            <rect width="{a4_width / scale}" height="{a4_height / scale}" fill="white" stroke="black" stroke-width="2"/>
        '''


def main():
    character_info: list[Character] = []

    with open("characters.json") as f:
        reminder_tokens_info = json.load(f)

    # Read each character's JSON file and generate SVGs
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
    character_name_description_map = {i.name: i for i in character_info}

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

    reminder_tokens = [i for i in reminder_tokens if i.name != "No ability"]

    all_infos = character_info + reminder_tokens

    page_height = a4_height / scale
    page_width = a4_width / scale

    with open("characters.html", "w") as html_file:
        html_file.write("""<!DOCTYPE html><head><meta charset="utf-8"></head><body>""")
        html_file.write(get_page_start_html())
        y = 20
        x = 20
        index = 0
        last_row_max_height = 0
        even_row = True

        while index < len(all_infos):
            # Generate the main SVG content

            svg_content = ""
            if isinstance(all_infos[index], Character):
                if x + svg_width > page_width - 20:
                    x = 20
                    y += last_row_max_height
                    last_row_max_height = 0

                    if even_row:
                        even_row = False
                        x = 20 + svg_width / 2 + 10
                    else:
                        even_row = True
                else:
                    svg_content = generate_character_svg(all_infos[index], x, y)
                    x += svg_width + 20
                    last_row_max_height = max(
                        last_row_max_height, svg_height + 20 - vertical_squish
                    )
            else:
                if x + svg_width / 2 > page_width - 20:
                    x = 20
                    y += last_row_max_height
                    last_row_max_height = 0
                else:
                    svg_content = generate_reminder_tokens(
                        all_infos[index].character.image,
                        all_infos[index].name,
                        all_infos[index].has_daytime_effect,
                        all_infos[index].drunk_or_poisoned,
                        x,
                        y,
                    )
                    x += reminder_token_width + 20
                    last_row_max_height = max(
                        last_row_max_height, svg_height / math.sqrt(2) - 10
                    )

            if svg_content:
                html_file.write(svg_content)
                index += 1

            if (
                index < len(all_infos)
                and y
                > page_height
                - (
                    svg_height
                    if isinstance(all_infos[index], Character)
                    else svg_height / math.sqrt(2) - 10
                )
                - 20
            ):
                html_file.write("</svg>")
                html_file.write(get_page_start_html())

                y = 20

            # Calculate positions for each character SVG
            # for index, character in enumerate(page):
            #     # Calculate x and y positions based on index
            #     if index % 7 < 4:  # 4 characters on odd rows
            #         x = (index % 7) * (svg_width + 20) + margin  # 20px margin
            #         y = (index // 7) * 2 * (svg_height + 20 - vertical_squish) + margin
            #     else:  # 3 characters on even rows
            #         x = (index % 7 - 4 + 0.5) * (svg_width + 20) + margin
            #         y = ((index // 7) * 2 + 1) * (
            #             svg_height + 20 - vertical_squish
            #         ) + margin

            # svg_content += """
            # </svg>
            # """

            # html += svg_content

        html_file.write("</body></html>")

    print("SVG file generated successfully: characters.html")


if __name__ == "__main__":
    main()
