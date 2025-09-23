import get_characters
import json
import itertools
import re
import os
import collections

Reminder = collections.namedtuple("Reminder", ["name", "description", "image", "team"])
Script = collections.namedtuple(
    "Script",
    [
        "name",
        "author",
        "characters",
        "jinxes",
        "layout",
        "show_player_counts",
        "spacers",
        "size"
    ],
)
Jinx = collections.namedtuple("Jinx", ["name", "team", "image", "description", "id"])


def escape(e):
    return e.translate({ord("<"): "&lt;", ord('"'): "&quot;", ord("&"): "&amp;"})


characters_per_category = {
    "Demons": [1 for i in range(5, 15)],
    "Minions": [1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3],
    "Outsiders": [0, 1, 0, 1, 2, 0, 1, 2, 0, 1, 2],
    "Townsfolk": [3, 3, 5, 5, 5, 7, 7, 7, 9, 9, 9],
}


def or_seperate(z):
    z = [*z]
    if len(z) > 1:
        return ", ".join(z[:-1]) + " or " + z[-1]
    else:
        return z[0]


def group_demons(night_order):
    demons = []
    demon_start_index = 0
    for index, (name, reminder, image, team) in enumerate(night_order):
        if (
            team == "demon"
            and demon_start_index in (0, index - len(demons))
            and (
                match := re.match(
                    r"<span>The (([A-Z]\w+)( [A-Z]\w+)*) chooses a player\. <span class=\"reminder-token\"></span>",
                    reminder,
                )
            )
        ):
            if demon_start_index == 0:
                demon_start_index = index
            demons.append(
                Reminder(
                    name=name,
                    description=reminder.replace(match[0], "<span>"),
                    image=image,
                    team=team,
                )
            )

    if len(demons) > 1:
        del night_order[demon_start_index : demon_start_index + len(demons)]
        night_order.insert(
            demon_start_index,
            Reminder(
                name=None,
                description=f'<span>The {or_seperate(i.name for i in demons)} choose a player. <span class="reminder-token"></span>',
                image=[i.image for i in demons],
                team="demon",
            ),
        )
        for demon in demons:
            if not re.match("<span>\\s*</span>", demon.description):
                night_order.insert(demon_start_index + 1, demon)

    return night_order


def very_basic_markdown(e):
    t = re.sub(
        r"\*(.*?)\*",
        lambda i: '<span class="reminder-token-name">' + escape(i[1]) + "</span>",
        e,
    )
    t = t.replace(":reminder:", '<span class="reminder-token"></span>')
    return "<span>" + t + "</span>"


def get_scrips(characters):
    with open("jinx.json") as f:
        jinxes = {
            i["id"]: {j["id"]: j["reason"] for j in i["jinx"]} for i in json.load(f)
        }

    names = os.listdir("scripts_json")
    for name in names:
        with open(f"scripts_json/{name}") as f:
            content = json.load(f)

            script_characters = [
                i
                for i in [
                    characters[
                        (
                            i if isinstance(i, str) else i.get("id", i.get("_id"))
                        ).replace("_", "")
                    ]
                    for i in content[1:]
                ]
                if i.team != "traveller"
            ]

            script_jinxes = sorted(
                [
                    (i, j, jinxes[i.id][j.id])
                    for i in script_characters
                    for j in script_characters
                    if i.id in jinxes and j.id in jinxes[i.id]
                ],
                key=lambda i: len(i[2]),
            )

            yield Script(
                name=content[0]["name"],
                author=content[0]["author"],
                characters=[
                    *script_characters,
                ]
                + [
                    Jinx(
                        name=" & ".join(i.name for i in jinx[:2]),
                        image=[i.image for i in jinx[:2]],
                        team="jinx",
                        description=jinx[2],
                        id="-".join(i.id for i in jinx[:2])
                    )
                    for jinx in script_jinxes
                ],
                jinxes=script_jinxes,
                layout=content[0].get("layout", {}),
                show_player_counts=content[0].get("show_player_counts", True),
                spacers=set(content[0].get("spacers", [])),
                size=content[0].get("size", "full")
            )


def main():
    characters = {i.id: i for i in get_characters.get_character_tokens("characters")}
    scripts = sorted(get_scrips(characters), key=lambda i:(i.size, i.name))

    with open("BOTC Roles September 2025.json") as night_order_file:
        night_order = {i["name"]: i for i in json.load(night_order_file)}
    
    page = "left"

    with open(f"scripts/all.html", "w") as f:
        f.write(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/paper-css/0.4.1/paper.css">
                <link rel="stylesheet" href="../style.css">
                <style>
                    @page {{
                        size: A4 landspace;
                    }}
                </style>
            </head>
            <body class="A4 landscape">
        """)

        for script in scripts:
            if script.size == "full":
                f.write("""<section class="sheet" style="padding: 5mm">""")
            elif page == "left":
                f.write("""<section class="sheet two-page-sheet">""")

            if script.size == "half":
                f.write("""<div class="half-page">""")

            f.write(
                f'''
                <div style="top: 5mm; right: 5mm; position: absolute">* not the first night</div>
                <h1>{escape(script.name)}</h1>'''
            )

            f.write('<div class="columns">')

            for group, category_character in itertools.groupby(
                script.characters, lambda i: i.team
            ):
                if layout := script.layout.get(group):
                    top, left, width, height = layout
                    layout_style = f"grid-row: {top} / span {height}; grid-column: {left} / span {width}"
                else:
                    layout_style = ""

                f.write(f"""
                <div class="subgrid {group}" style="{layout_style}">
                <div class="title-container">
                    <h2>{group}</h2>
                </div>""")

                for character in category_character:
                    if character.id in script.spacers:
                        f.write("<div></div>")

                    if isinstance(character.image, str):
                        img = f"""<img src="../{escape(character.image)}">"""
                    else:
                        img = (
                            f"""<div class='jinx-image'>"""
                            + "".join(
                                f'<img src="../{escape(i)}">' for i in character.image
                            )
                            + "</div>"
                        )

                    f.write(f"""
                        <div class="character">
                            {img}
                            <h3>{escape(character.name)}</h3>
                            <p>{escape(character.description)}</p>
                        </div>
                    """)

                f.write("""</div>""")

            f.write("</div>")

            if script.show_player_counts:
                f.write("""
                    <table layout="fixed">
                        <tr>
                            <th colspan="2">Residents</th>

                            <th>5</th>
                            <th>6</th>
                            <th>7</th>
                            <th>8</th>
                            <th>9</th>
                            <th>10</th>
                            <th>11</th>
                            <th>12</th>
                            <th>13</th>
                            <th>14</th>
                            <th>15</th>
                        </tr>

                        <tr>
                            <th colspan="2">Townsfolk</th>

                            <td colspan="2">3</td>
                            <td colspan="3">5</td>
                            <td colspan="3">7</td>
                            <td colspan="3">9</td>
                        </tr>

                        <tr>
                            <th colspan="2">Outsiders</th>

                            <td>0</td>
                            <td>1</td>
                            <td>0</td>
                            <td>1</td>
                            <td>2</td>
                            <td>0</td>
                            <td>1</td>
                            <td>2</td>
                            <td>0</td>
                            <td>1</td>
                            <td>2</td>
                        </tr>

                        <tr>
                            <th colspan="2">Minions</th>
                            <td colspan="5">1</td>
                            <td colspan="3">2</td>
                            <td colspan="3">3</td>
                        </tr>
                    </table>
                """)

            if script.size == "half":
                f.write("""</div>""")

            if script.size == "full":
                f.write("</section>")
                page = "left"
            elif page == "left":
                page = "right"
            else:
                page = "left"
        f.write("</body></html>")
    with open("scripts/night_order.html", "w") as f:
        f.write(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/paper-css/0.4.1/paper.css">
                <link rel="stylesheet" href="../style.css">
            </head>
            <body class="A4 portrait">
        """)

        for script in scripts:
            script_characters = {i.name: i for i in script.characters}

            def get_reminders(name, order):
                return group_demons(
                    sorted(
                        (
                            Reminder(
                                name=i,
                                description=very_basic_markdown(night_order[i][name]),
                                image="../" + script_characters[i].image
                                if i in script_characters
                                else {
                                    "Dawn": "../images/dawn.svg",
                                    "Dusk": "../images/dusk.svg",
                                    "Minion Info": "../images/minion.svg",
                                    "Demon Info": "../images/demon.svg",
                                }[i],
                                team=night_order[i].get("team", "special"),
                            )
                            for i in [
                                *script_characters.keys(),
                                "Dawn",
                                "Dusk",
                                "Minion Info",
                                "Demon Info",
                            ]
                            if i in night_order
                            if name in night_order[i] and night_order[i][name]
                        ),
                        key=lambda i: night_order[i.name][order],
                    )
                )

            first_night_reminders = get_reminders("firstNightReminder", "firstNight")
            other_night_reminders = get_reminders("otherNightReminder", "otherNight")

            f.write(
                f'''<section class="sheet" style="padding: 5mm; position: relative">
                <h1>{escape(script.name)}</h1>'''
            )

            f.write('<div class="night-order-layout">')

            for title, reminders, style in (
                ("First Night", first_night_reminders, ""),
                ("Other Nights", other_night_reminders, "transform: rotate(180deg)"),
            ):
                f.write(f'''<div class="first-night" style="{escape(style)}">
                
                    <h2>{title}</h2>
                ''')

                for name, reminder, image, team in reminders:
                    color = (
                        "#281f36"
                        if name == "Dusk"
                        else "#b8822a"
                        if name == "Dawn" or team == "fabled"
                        else "#13b318"
                        if team not in ("townsfolk", "outsider", "demon", "minion")
                        else "#009bca"
                        if team in ("townsfolk", "outsider")
                        else "#b31318"
                    )

                    if isinstance(image, str):
                        image = f"""<img src="{escape(image)}"
                                style="{"transform: scale(0.7)" if image.endswith(".svg") else ""}"
                            >"""
                    else:
                        image = (
                            '<div class="small-demon-image-grid">'
                            + "".join(
                                f"""<img src="{escape(i)}" class="small">"""
                                for i in image
                            )
                            + "</div>"
                        )

                    f.write(f"""
                        <div class="reminder" style="--color: {color}">
                            <div style="border-right: 1mm solid var(--color)">
                                {image}
                            </div>
                            <p>{reminder}</p>
                        </div>
                    """)

                f.write("</div>")

                if title == "First Night":
                    f.write('<div class="fancy-decoration"></div>')
            f.write("</div>")
            f.write("</section>")


if __name__ == "__main__":
    main()
