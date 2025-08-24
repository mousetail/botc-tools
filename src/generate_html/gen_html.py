import math
import itertools

from svg_tools import generate_reminder_tokens, generate_character_svg
from get_characters import (
    get_character_tokens,
    get_reminder_tokens,
    Character,
    expand_iterable,
)
from constants import (
    a4_width,
    a4_height,
    circle_radius,
    scale,
    svg_width,
    svg_height,
    vertical_squish,
    reminder_token_width,
    horizontal_margin,
    verrtical_margin,
    horizontal_space_between_tokens,
)

# Define the path to the characters folder
characters_folder = "characters"


def get_page_start_html(page_number):
    return f'''
        <svg width="{a4_width}" height="{a4_height}" viewBox="0 0 {a4_width / scale} {a4_height / scale}" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <clipPath id="circleClip">
                    <circle cx="{circle_radius}" cy="{circle_radius}" r="{circle_radius}" />
                </clipPath>
            </defs>
            <rect width="{a4_width / scale}" height="{a4_height / scale}" fill="white" stroke="black" stroke-width="2"/>
            <text x="15" y="30" font-size="12" fill="black">{page_number}</text>
        '''


def main():
    character_info = get_character_tokens(characters_folder)
    reminder_tokens = get_reminder_tokens(character_info)

    all_infos = expand_iterable(itertools.chain(character_info, reminder_tokens))

    page_height = a4_height / scale
    page_width = a4_width / scale

    page_number = 1

    with open("characters.html", "w") as html_file:
        html_file.write("""<!DOCTYPE html><head><meta charset="utf-8"></head><body>""")
        html_file.write(get_page_start_html(page_number))
        y = verrtical_margin
        x = horizontal_margin
        last_row_max_height = 0
        even_row = True

        token = next(all_infos)

        

        while True:
            # Generate the main SVG content

            svg_content = ""
            if isinstance(token, Character):
                if x + svg_width > page_width - 20:
                    x = horizontal_margin
                    y += last_row_max_height
                    last_row_max_height = 0

                    if even_row:
                        even_row = False
                        x = 20 + svg_width / 2 + horizontal_space_between_tokens / 2
                    else:
                        even_row = True
                else:
                    svg_content = generate_character_svg(token, x, y)
                    x += svg_width + horizontal_space_between_tokens
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
                        token.character.image,
                        token.name,
                        token.has_daytime_effect,
                        token.drunk_or_poisoned,
                        x,
                        y,
                    )
                    x += reminder_token_width + 20
                    last_row_max_height = max(
                        last_row_max_height, svg_height / math.sqrt(2) - 10
                    )

            if svg_content:
                html_file.write(svg_content)
                try:
                    token = next(all_infos)
                except StopIteration:
                    break

            if (
                y
                > page_height
                - (
                    svg_height
                    if isinstance(token, Character)
                    else svg_height / math.sqrt(2) - 10
                )
                - 20
            ):
                html_file.write("</svg>")
                page_number += 1
                html_file.write(get_page_start_html(page_number))

                even_row = True
                x = horizontal_margin
                y = verrtical_margin

        html_file.write("</body></html>")

    print("SVG file generated successfully: characters.html")


if __name__ == "__main__":
    main()
