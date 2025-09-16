import re
import functools
import math
from constants import (
    svg_width,
    reminder_token_width,
    font_size,
    circle_radius,
    description_max_width,
    horizontal_margin,
    verrtical_margin,
)


def get_token_style():
    return """
        stroke="black"
        stroke-width="1"
        fill="white"
    """


def xml_escape(text):
    """Escape special characters for XML."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def generate_text_path(id, radius, arc, script):
    side = 1 if arc else -1

    if script == "fabled":
        return f"""
            <path
                id="{id}"
                d="M -60 {-(radius - 5) * side} L 60 {-(radius - 5) * side}"
            />
        """

    return f"""<path
        id="{id}"
        d="M {-radius * math.sqrt(2) / 2} {radius * math.sqrt(2) * side / 2}
           A {radius} {radius} 0 1 {arc} {radius * math.sqrt(2) / 2} {radius * math.sqrt(2) * side / 2}"
        fill="none"
    />
    """


def estimate_proportional_length_in_pixels(text):
    """Estimate the length of a string in pixels for a variable-width font."""
    # Character width mapping using sets for grouping
    char_widths = {
        2: set("ilftjrs"),
        3: set(" ,!?-:;()[]{}<>@"),
        4: set("acegknpqxyzAEFGHJKLMNPRUVW"),
        5: set("bcdhuwvBDEHIOQSTYZ"),
        6: set("mM"),
        7: set("W"),
    }

    width_mapping = {
        char: width for width, chars in char_widths.items() for char in chars
    }

    estimated_length = sum(width_mapping.get(char, 5) for char in text)

    return estimated_length


def generate_background_shape(script):
    radius = circle_radius * 1.35
    side = 1

    if script == "fabled":
        short_axis = math.sin(math.radians(30)) * radius
        long_axis = math.cos(math.radians(30)) * radius

        return f"""
            <path
                {get_token_style()}
                d="
                   M 0 {long_axis * side}
                   L {-short_axis} {long_axis * side}
                   L {-radius} 0
                   L {-short_axis} {-long_axis * side}
                   L {short_axis} {-long_axis * side}
                   L {radius} 0
                   L {short_axis} {long_axis * side}
                   Z
                "
            />
        """
    return f"""<circle cx="0" cy="0" r="{svg_width / 2}" 
                {get_token_style()}/>"""


def split_string_in_lines_on_regex(string, character, max_length):
    parts = re.split(character, string)

    e = [
        i
        for i in functools.reduce(
            lambda current, part: current[:-1] + [current[-1] + part]
            if estimate_proportional_length_in_pixels(current[-1] + part)
            <= max_length(len(current))
            else current + [part],
            parts,
            [""],
        )
        if i
    ]

    return e


# Function to generate SVG for a character
def generate_character_svg(character, x, y):
    description_parts = split_string_in_lines_on_regex(
        character.description,
        "(?<= )" if character.script == "fabled" else "(?<=[,.:&)])",
        lambda i: description_max_width // 2.2 - 6 + 6 * i
        if character.script == "fabled"
        else description_max_width,
    )

    text = "\n".join(
        [
            f"""<textPath href="#{character.name}-textPathBottom{index + 1}" startOffset="50%" text-anchor="middle" white-space="wrap">{xml_escape(part)}</textPath>"""
            for index, part in enumerate(description_parts)
        ]
    )

    svg = f'''
    <g transform="translate({x + svg_width / 2}, {y + svg_width / 2}) rotate(15)">
        <defs>
            <clipPath id="circleClipTop">
                <circle cx="0" cy="0" r="{circle_radius}" />
            </clipPath>
            {generate_text_path(character.name + "-textPathTop", circle_radius, 0, character.script)}

            {generate_text_path(character.name + "-textPathBottom1", circle_radius + 5, 1, character.script)}
            {generate_text_path(character.name + "-textPathBottom2", circle_radius - 5, 1, character.script)}
            {generate_text_path(character.name + "-textPathBottom3", circle_radius - 15, 1, character.script)}
            {generate_text_path(character.name + "-textPathBottom4", circle_radius - 25, 1, character.script)}
        </defs>
        {generate_background_shape(character.script)}
        <image href="../{character.image}" x="{-circle_radius}" y="{-circle_radius}" width="{circle_radius * 2}" height="{circle_radius * 2}" />
        <text fill="black" font-size="{font_size * (0.7 if character.script == "fabled" else 1.0)}" font-family="Dumbledor">
            <textPath href="#{character.name}-textPathTop" startOffset="50%" text-anchor="middle">{xml_escape(character.name)}</textPath>
        </text>
        <text fill="black" font-size="{font_size / 3}">
            {text}
        </text>
    </g>
    '''
    return svg


def reminder_token_shape():
    height = math.sqrt(2) * circle_radius
    return f"""M 0, {height / 2} 
            A {circle_radius}, {circle_radius} 0 0, 0 0, {-height / 2} 
            L {reminder_token_width} {-height / 2} 
            A {circle_radius}, {circle_radius} 0 0, 1 {reminder_token_width}, {height / 2} 
            Z"""


def generate_reminder_tokens(image, name, has_daytime_effect, drunk_or_poisoned, x, y):
    radius = circle_radius
    height = math.sqrt(2) * circle_radius

    svg = f"""
    <g transform="translate({x} {y + height})">
        <path d="{reminder_token_shape()}"
            {
        get_token_style()
        if image
        else 'fill="#b31318"'
        if name == "Evil"
        else 'fill="#009bca"'
        if name == "Good"
        else 'fill="black"'
    }
        />
        {
        generate_normal_reminder_token(
            image, name, has_daytime_effect, drunk_or_poisoned
        )
        if image
        else generate_special_token(name)
    }
    </g>
    """
    return svg


def generate_normal_reminder_token(image, name, has_daytime_effect, drunk_or_poisoned):
    words = [
        j
        for i in name.replace("Is the", "Is\u00a0the").split(" ")
        for j in ([i] if len(i) > 1 else ["", i])
    ]

    height = math.sqrt(2) * circle_radius
    return f"""
        <g {
        f'transform="translate({reminder_token_width * 1.5 + 2}) rotate(180)"'
        if has_daytime_effect and not drunk_or_poisoned
        else ""
    }>
            <image
                href="../{image}"
                x="{reminder_token_width / 2 - circle_radius / 3 + 20}"
                y="{-height / 4 - circle_radius / 3}"
                width="{circle_radius / 1.5}" height="{circle_radius / 1.5}"
                transform-origin="{reminder_token_width / 2 + 20} {-height / 4}"
                {'transform="rotate(90)"' if drunk_or_poisoned else ""}
            />
            {
        "".join(
            f'''<text
                        fill="{"black" if image is not None else "white"}"

                        transform-origin="
                            {reminder_token_width / 2 + 20 if image is not None else 0}
                            {height / 4 + 10 * index - 5 * len(words)}
                        "
                        x="{reminder_token_width / 2 + 20}"
                        y="{height / 4 + 10 * index - 5 * len(words)}"

                        {'transform="rotate(90)"' if drunk_or_poisoned else ""}
                        font-size="{
                font_size * 1.5
                if image is None
                else font_size / 2
                if len(name) > 1
                else font_size
            }"
                        {'font-family="Dumbledor"' if len(name) < 2 else ""}
                        text-anchor="middle"
                    >
                    {xml_escape(name)}
                </text>'''
            for index, name in enumerate(words)
        )
    }
    </g>
    """


def generate_special_token(name):
    height = math.sqrt(2) * circle_radius
    id = name.lower().replace(" ", "-") + "-reminder-token"

    offset = 25

    return f"""
        <defs>
            <path
                id="{id}"
                d="
                    M {reminder_token_width - offset}, {height / 2} 
                    A {circle_radius}, {circle_radius} 0 0, 0 {reminder_token_width - offset}, {-height / 2}
                "
            />
        </defs>
        <text fill="white" font-size="{font_size * 1.5}" letter-spacing="3" font-family="Dumbledor">
            <textPath href="#{id}" startOffset="50%" text-anchor="middle">{xml_escape(name)}</textPath>
        </text>
    """
    pass
