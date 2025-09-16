import math
import itertools
import functools

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

            <style>
                @font-face {{
                    font-family: 'Dumbledor';
                    src: url('../dumbledor.woff2') format('woff2');
                    font-weight: normal;
                    font-style: normal
                }}
            </style>

            <defs>
                <clipPath id="circleClip">
                    <circle cx="{circle_radius}" cy="{circle_radius}" r="{circle_radius}" />
                </clipPath>
            </defs>
            <rect width="{a4_width / scale}" height="{a4_height / scale}" fill="white" stroke="black" stroke-width="2"/>
            <text x="15" y="30" font-size="12" fill="black">{page_number}</text>
        '''


def generate_pages(character_tokens, reminder_tokens):
    all_infos = expand_iterable(itertools.chain(character_tokens, reminder_tokens))
    page = []

    y = verrtical_margin
    x = horizontal_margin
    last_row_max_height = 0
    even_row = True

    page_height = a4_height / scale
    page_width = a4_width / scale

    token = next(all_infos)

    while True:
        # Generate the main SVG content
        generate_svg_fn = None

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
                generate_svg_fn = functools.partial(generate_character_svg, token, x, y)
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
                generate_svg_fn = functools.partial(
                    generate_reminder_tokens,
                    token.character and token.character.image,
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

        if generate_svg_fn:
            page.append(generate_svg_fn)
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
            yield page
            page = []

            even_row = True
            x = horizontal_margin
            y = verrtical_margin
    if page:
        yield page


def main():
    character_tokens = get_character_tokens(characters_folder)
    reminder_tokens = get_reminder_tokens(character_tokens)

    with open("characters.html", "w") as html_file:
        html_file.write(
            '<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>'
        )
        html_file.write(f"""
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                }}
                body {{
                    margin: 0;
                }}

                
            </style>
        """)
        for page_number, page in enumerate(
            generate_pages(character_tokens, reminder_tokens)
        ):
            file_name = f"page_svgs/{page_number + 1}.svg"
            with open(file_name, "w") as svg_file:
                svg_file.write(get_page_start_html(page_number + 1))

                for token in page:
                    svg_file.write(token())
                svg_file.write("</svg>")

            html_file.write(
                f'<object data="{file_name}" style="page-break-after: always; display: block; width: 100vw; height: 100vh"></object>'
            )

        html_file.write("</body></html>")

    print("SVG file generated successfully: characters.html")


if __name__ == "__main__":
    main()
