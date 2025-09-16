import get_characters
import json
import itertools
import re


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
    grid-template-columns: 4rem 25rem;

    & .small-demon-image-grid {
        width: 3.75rem;
        height: 3.75rem;

        & img {
            width: 50%;
            height: 50%;
            transform: scale(1.5)
        }
    }

    & img {
        width: 3.75rem;
        meight: 3.75rem;
    }

    & p {
        margin-bottom: 1rem;
        text-align: justify;
    }
}

.night-order-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
}
"""


def group_demons(night_order):
    demons = []
    demon_start_index = 0
    for index, (reminder, image) in enumerate(night_order):
        if demon_start_index in (0, index - len(demons)) and (
            match := re.match(
                r"<span>The (([A-Z]\w+)( [A-Z]\w+)*) points to a player. That player dies.",
                reminder,
            )
        ):
            if demon_start_index == 0:
                demon_start_index = index
            demons.append((reminder.replace(match[0], "<span>"), image))

    if len(demons):
        del night_order[demon_start_index : demon_start_index + len(demons)]
        night_order.insert(
            demon_start_index,
            (
                "<span>The demon points to a player. That player dies.</span>",
                [i[1] for i in demons],
            ),
        )
        for demon in demons:
            if not re.match("<span>\\s*</span>", demon[0]):
                print(demon[0])
                night_order.insert(demon_start_index + 1, demon)

    return night_order


def main():
    characters = get_characters.get_character_tokens("characters")

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

        for script, script_characters in itertools.groupby(
            characters, lambda i: i.script
        ):
            if script in ("fabled", "experimental", "travellers"):
                continue

            f.write(
                f'<section class="sheet" style="padding: 5mm"><h1>{escape(script)}</h1>'
            )

            # print(script)
            for group, category_character in itertools.groupby(
                script_characters, lambda i: i.category
            ):
                # print('\t'+group)
                f.write(f"""<div class="title-container">
                    <h2>{group}</h2>
                </div><div class="columns">""")

                for character in category_character:
                    f.write(f"""<div class="character">
                        <img src="../{escape(character.image)}">
                        <h3>{escape(character.name)}</h3>
                        <p>{escape(character.description)}</p>
                    </div>""")
                    # print('\t\t'+character.name)

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

        for script, script_characters in itertools.groupby(
            characters, lambda i: i.script
        ):
            script_characters = {i.name: i for i in script_characters}

            with open("night_order.json") as night_order_file:
                night_order = json.load(night_order_file)

            first_night_reminders = [
                (
                    i["description"],
                    "../" + script_characters[i["name"]].image
                    if i["name"] in script_characters
                    else "",
                )
                for i in night_order["first_night_info"]
                if i["name"] in script_characters
                or i["name"] in ("Demon Info", "Minion Info")
            ]
            other_night_reminders = group_demons(
                [
                    (
                        i["description"],
                        "../" + script_characters[i["name"]].image
                        if i["name"] in script_characters
                        else "",
                    )
                    for i in night_order["other_nights_info"]
                    if i["name"] in script_characters
                    or i["name"] in ("Demon Info", "Minion Info")
                ]
            )

            f.write(
                f'<section class="sheet" style="padding: 5mm"><h1>{escape(script)}</h1>'
            )

            f.write('<div class="night-order-layout">')

            for title, reminders, style in (
                ("First Night", first_night_reminders, ""),
                ("Other Nights", other_night_reminders, "transform: rotate(180deg)"),
            ):
                f.write(f'''<div class="first-night" style="{escape(style)}">
                
                    <h2>{title}</h2>
                ''')

                for reminder, image in reminders:
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
                        <div class="reminder">
                            {image}
                            <p>{reminder}</p>
                        </div>
                    """)

                f.write("</div>")
            f.write("</div>")
            f.write("</section>")


if __name__ == "__main__":
    main()
