import get_characters
import json
import itertools
import re
import os
import collections

Reminder = collections.namedtuple("Reminder", ["name", "description", "image", "team"])
Script = collections.namedtuple("Script", ["name", "author", "characters"])


def escape(e):
    return e.translate({ord("<"): "&lt;", ord('"'): "&quot;", ord("&"): "&amp;"})


characters_per_category = {
    "Demons": [1 for i in range(5, 15)],
    "Minions": [1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3],
    "Outsiders": [0, 1, 0, 1, 2, 0, 1, 2, 0, 1, 2],
    "Townsfolk": [3, 3, 5, 5, 5, 7, 7, 7, 9, 9, 9],
}

css = """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html {
    font-size: 12.5px;
}

@page {
    size: A4;
    margin: 1em;
}

@font-face {
    font-family: 'Dumbledor';
    src: url('../dumbledor.woff2') format('woff2');
    font-weight: normal;
    font-style: normal
}

h1, h2, h3 {
    font-family: 'Dumbledor';
}

h1 {
    display: block;
    margin: auto;
    text-align: center;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
    color: #4f0e10
}

h3 {
    font-size: 1.1rem;
}

p {
    font-size: 0.8rem;
}

.title-container {
    border-bottom: 2px solid #4f0e10;
    position: relative;
    height: 0;
    margin-bottom: 0.9rem;

    & h2 {
        font-size: 0.8rem;
        display: block;
        background-color: white;
        right: 4rem;
        top: -1rem;
        width: 7rem;
        height: 2rem;
        padding: 0.45rem;
        border: 2px solid #4f0e10;
        border-radius: 1rem;
        position: absolute;
        text-align: center;
        color:  #4f0e10;
    }
}

.columns {
    display: grid;
    grid-template-columns: repeat(auto-fill, 21.5rem);
    gap: 0.25rem;
}

.character {
    display: grid;
    grid-template-columns: 5rem 16.5rem;
    grid-template-rows: 1.5rem 5rem;

    & h3 {
        margin: 0;
        break-after: avoid;
    }

    & p {
        margin: 0;
        text-align: justify;
    }

    & img {
        width: 3.75rem;
        height: 3.75rem;
        grid-row: 1 / span 2;
        transform: scale(1.6) translate(0.25rem, 0);
        transform-origin: center;
    }
}

table {
    table-layout: fixed;
    width: 50%;
    border-collapse: collapse;
    margin: auto;

    & td:not(:last-child) {
        border-right: 1px solid black;
    }

    & td {
        text-align: center;
    }
}

.reminder {
    display: grid;
    grid-template-columns: 3.75rem 1fr;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
    align-items: center;

    & .small-demon-image-grid {
        width: 3.75rem;
        height: 3.75rem;

        & img {
            width: 49%;
            height: 49%;
            transform: scale(1.3);
        }
    }

    & img {
        width: 3rem;
        height: 3rem;
        transform: scale(1.2);
    }

    & p {
        text-align: justify;
        font-size: 0.7rem;
    }
}

.night-order-layout {
    display: grid;
    grid-template-columns: 1fr 0.5rem 1fr;
    gap: 1rem;

    &>div {
        height: calc(296mm - 8rem);

        &>h2 {
            text-align: center;
        }
    }

    & .fancy-decoration {
        background-image: url('../images/vertical_rule.svg');
        background-position: center;
        background-repeat: no-repeat;
        background-size: 2rem;
    }
}

span.reminder-token {
    display: inline-block;
    width: 0.75rem;
    height: 0.75rem;
    background: var(--color);
    border-radius: 0.375rem;
    break-before: avoid;
    vertical-align: middle;
}

.reminder-token-name {
    color: var(--color);
    text-decoration-thickness: 0.5mm;
}
"""


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
    names = os.listdir("scripts_json")
    for name in names:
        with open(f"scripts_json/{name}") as f:
            content = json.load(f)
            yield Script(
                name=content[0]["name"],
                author=content[0]["author"],
                characters=[
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
                ],
            )


def main():
    characters = {i.id: i for i in get_characters.get_character_tokens("characters")}
    scripts = [*get_scrips(characters)]

    with open("BOTC Roles September 2025.json") as night_order_file:
        night_order = {i["name"]: i for i in json.load(night_order_file)}

    with open(f"scripts/all.html", "w") as f:
        f.write(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/paper-css/0.4.1/paper.css">
                <style>{css}
                </style>
            </head>
            <body class="A4 landscape">
        """)

        for script in scripts:
            f.write(
                f'<section class="sheet" style="padding: 5mm"><h1>{escape(script.name)}</h1>'
            )

            for group, category_character in itertools.groupby(
                script.characters, lambda i: i.category
            ):
                f.write(f"""<div class="title-container">
                    <h2>{group}</h2>
                </div><div class="columns">""")

                for character in category_character:
                    f.write(f"""<div class="character">
                        <img src="../{escape(character.image)}">
                        <h3>{escape(character.name)}</h3>
                        <p>{escape(character.description)}</p>
                    </div>""")

                f.write("</div>")

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

            f.write("</section>")
        f.write("</body></html>")
    with open("scripts/night_order.html", "w") as f:
        f.write(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/paper-css/0.4.1/paper.css">
                <style>{css}
                </style>
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
                f'<section class="sheet" style="padding: 5mm"><h1>{escape(script.name)}</h1>'
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
                        if name == "Dawn"
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
