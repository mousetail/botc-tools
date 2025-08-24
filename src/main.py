import requests
from bs4 import BeautifulSoup
import os
import json
import time
import random

EXPERIMENTAL_CHARACTERS = [
    "https://wiki.bloodontheclocktower.com/Acrobat",
    "https://wiki.bloodontheclocktower.com/Al-Hadikhia",
    "https://wiki.bloodontheclocktower.com/Alchemist",
    "https://wiki.bloodontheclocktower.com/Alsaahir",
    "https://wiki.bloodontheclocktower.com/Amnesiac",
    "https://wiki.bloodontheclocktower.com/Atheist",
    "https://wiki.bloodontheclocktower.com/Balloonist",
    "https://wiki.bloodontheclocktower.com/Banshee",
    "https://wiki.bloodontheclocktower.com/Boffin",
    "https://wiki.bloodontheclocktower.com/Boomdandy",
    "https://wiki.bloodontheclocktower.com/Bootlegger",
    "https://wiki.bloodontheclocktower.com/Bounty_Hunter",
    "https://wiki.bloodontheclocktower.com/Cacklejack",
    "https://wiki.bloodontheclocktower.com/Cannibal",
    "https://wiki.bloodontheclocktower.com/Choirboy",
    "https://wiki.bloodontheclocktower.com/Cult_Leader",
    "https://wiki.bloodontheclocktower.com/Damsel",
    "https://wiki.bloodontheclocktower.com/Deus_ex_Fiasco",
    "https://wiki.bloodontheclocktower.com/Engineer",
    "https://wiki.bloodontheclocktower.com/Farmer",
    "https://wiki.bloodontheclocktower.com/Fearmonger",
    "https://wiki.bloodontheclocktower.com/Ferryman",
    "https://wiki.bloodontheclocktower.com/Fisherman",
    "https://wiki.bloodontheclocktower.com/Gangster",
    "https://wiki.bloodontheclocktower.com/Gardener",
    "https://wiki.bloodontheclocktower.com/General",
    "https://wiki.bloodontheclocktower.com/Gnome",
    "https://wiki.bloodontheclocktower.com/Goblin",
    "https://wiki.bloodontheclocktower.com/Golem",
    "https://wiki.bloodontheclocktower.com/Harpy",
    "https://wiki.bloodontheclocktower.com/Hatter",
    "https://wiki.bloodontheclocktower.com/Heretic",
    "https://wiki.bloodontheclocktower.com/Hermit",
    "https://wiki.bloodontheclocktower.com/High_Priestess",
    "https://wiki.bloodontheclocktower.com/Huntsman",
    "https://wiki.bloodontheclocktower.com/Kazali",
    "https://wiki.bloodontheclocktower.com/King",
    "https://wiki.bloodontheclocktower.com/Knight",
    "https://wiki.bloodontheclocktower.com/Legion",
    "https://wiki.bloodontheclocktower.com/Leviathan",
    "https://wiki.bloodontheclocktower.com/Lil%27_Monsta",
    "https://wiki.bloodontheclocktower.com/Lleech",
    "https://wiki.bloodontheclocktower.com/Lord_of_Typhon",
    "https://wiki.bloodontheclocktower.com/Lycanthrope",
    "https://wiki.bloodontheclocktower.com/Magician",
    "https://wiki.bloodontheclocktower.com/Marionette",
    "https://wiki.bloodontheclocktower.com/Mezepheles",
    "https://wiki.bloodontheclocktower.com/Nightwatchman",
    "https://wiki.bloodontheclocktower.com/Noble",
    "https://wiki.bloodontheclocktower.com/Ogre",
    "https://wiki.bloodontheclocktower.com/Ojo",
    "https://wiki.bloodontheclocktower.com/Organ_Grinder",
    "https://wiki.bloodontheclocktower.com/Pixie",
    "https://wiki.bloodontheclocktower.com/Plague_Doctor",
    "https://wiki.bloodontheclocktower.com/Politician",
    "https://wiki.bloodontheclocktower.com/Poppy_Grower",
    "https://wiki.bloodontheclocktower.com/Preacher",
    "https://wiki.bloodontheclocktower.com/Princess",
    "https://wiki.bloodontheclocktower.com/Psychopath",
    "https://wiki.bloodontheclocktower.com/Puzzlemaster",
    "https://wiki.bloodontheclocktower.com/Riot",
    "https://wiki.bloodontheclocktower.com/Shugenja",
    "https://wiki.bloodontheclocktower.com/Snitch",
    "https://wiki.bloodontheclocktower.com/Steward",
    "https://wiki.bloodontheclocktower.com/Storm_Catcher",
    "https://wiki.bloodontheclocktower.com/Summoner",
    "https://wiki.bloodontheclocktower.com/Village_Idiot",
    "https://wiki.bloodontheclocktower.com/Vizier",
    "https://wiki.bloodontheclocktower.com/Widow",
    "https://wiki.bloodontheclocktower.com/Wizard",
    "https://wiki.bloodontheclocktower.com/Wraith",
    "https://wiki.bloodontheclocktower.com/Xaan",
    "https://wiki.bloodontheclocktower.com/Yaggababble",
    "https://wiki.bloodontheclocktower.com/Zealot",
]
TROUBLE_BREWING_CHARACTERS = [
    "https://wiki.bloodontheclocktower.com/Washerwoman",
    "https://wiki.bloodontheclocktower.com/Librarian",
    "https://wiki.bloodontheclocktower.com/Investigator",
    "https://wiki.bloodontheclocktower.com/Chef",
    "https://wiki.bloodontheclocktower.com/Empath",
    "https://wiki.bloodontheclocktower.com/Fortune_Teller",
    "https://wiki.bloodontheclocktower.com/Undertaker",
    "https://wiki.bloodontheclocktower.com/Monk",
    "https://wiki.bloodontheclocktower.com/Ravenkeeper",
    "https://wiki.bloodontheclocktower.com/Virgin",
    "https://wiki.bloodontheclocktower.com/Slayer",
    "https://wiki.bloodontheclocktower.com/Soldier",
    "https://wiki.bloodontheclocktower.com/Mayor",
    "https://wiki.bloodontheclocktower.com/Butler",
    "https://wiki.bloodontheclocktower.com/Drunk",
    "https://wiki.bloodontheclocktower.com/Recluse",
    "https://wiki.bloodontheclocktower.com/Saint",
    "https://wiki.bloodontheclocktower.com/Poisoner",
    "https://wiki.bloodontheclocktower.com/Spy",
    "https://wiki.bloodontheclocktower.com/Scarlet_Woman",
    "https://wiki.bloodontheclocktower.com/Baron",
    "https://wiki.bloodontheclocktower.com/Imp",
]
SECTS_AND_VIOLETS_CHARACTERS = [
    "https://wiki.bloodontheclocktower.com/Clockmaker",
    "https://wiki.bloodontheclocktower.com/Dreamer",
    "https://wiki.bloodontheclocktower.com/Snake_Charmer",
    "https://wiki.bloodontheclocktower.com/Mathematician",
    "https://wiki.bloodontheclocktower.com/Flowergirl",
    "https://wiki.bloodontheclocktower.com/Town_Crier",
    "https://wiki.bloodontheclocktower.com/Oracle",
    "https://wiki.bloodontheclocktower.com/Savant",
    "https://wiki.bloodontheclocktower.com/Seamstress",
    "https://wiki.bloodontheclocktower.com/Philosopher",
    "https://wiki.bloodontheclocktower.com/Artist",
    "https://wiki.bloodontheclocktower.com/Juggler",
    "https://wiki.bloodontheclocktower.com/Sage",
    "https://wiki.bloodontheclocktower.com/Mutant",
    "https://wiki.bloodontheclocktower.com/Sweetheart",
    "https://wiki.bloodontheclocktower.com/Barber",
    "https://wiki.bloodontheclocktower.com/Klutz",
    "https://wiki.bloodontheclocktower.com/Evil_Twin",
    "https://wiki.bloodontheclocktower.com/Witch",
    "https://wiki.bloodontheclocktower.com/Cerenovus",
    "https://wiki.bloodontheclocktower.com/Pit-Hag",
    "https://wiki.bloodontheclocktower.com/Fang_Gu",
    "https://wiki.bloodontheclocktower.com/Vigormortis",
    "https://wiki.bloodontheclocktower.com/No_Dashii",
    "https://wiki.bloodontheclocktower.com/Vortox",
]
BAD_MOON_RISING_CHARACTERS = [
    "https://wiki.bloodontheclocktower.com/Grandmother",
    "https://wiki.bloodontheclocktower.com/Sailor",
    "https://wiki.bloodontheclocktower.com/Chambermaid",
    "https://wiki.bloodontheclocktower.com/Exorcist",
    "https://wiki.bloodontheclocktower.com/Innkeeper",
    "https://wiki.bloodontheclocktower.com/Gambler",
    "https://wiki.bloodontheclocktower.com/Gossip",
    "https://wiki.bloodontheclocktower.com/Courtier",
    "https://wiki.bloodontheclocktower.com/Professor",
    "https://wiki.bloodontheclocktower.com/Minstrel",
    "https://wiki.bloodontheclocktower.com/Tea_Lady",
    "https://wiki.bloodontheclocktower.com/Pacifist",
    "https://wiki.bloodontheclocktower.com/Fool",
    "https://wiki.bloodontheclocktower.com/Goon",
    "https://wiki.bloodontheclocktower.com/Lunatic",
    "https://wiki.bloodontheclocktower.com/Tinker",
    "https://wiki.bloodontheclocktower.com/Moonchild",
    "https://wiki.bloodontheclocktower.com/Godfather",
    "https://wiki.bloodontheclocktower.com/Devil%27s_Advocate",
    "https://wiki.bloodontheclocktower.com/Assassin",
    "https://wiki.bloodontheclocktower.com/Mastermind",
    "https://wiki.bloodontheclocktower.com/Zombuul",
    "https://wiki.bloodontheclocktower.com/Pukka",
    "https://wiki.bloodontheclocktower.com/Shabaloth",
    "https://wiki.bloodontheclocktower.com/Po",
]
TRAVELLER_CHARACTERS = [
    "https://wiki.bloodontheclocktower.com/Scapegoat",
    "https://wiki.bloodontheclocktower.com/Gunslinger",
    "https://wiki.bloodontheclocktower.com/Beggar",
    "https://wiki.bloodontheclocktower.com/Bureaucrat",
    "https://wiki.bloodontheclocktower.com/Thief",
    "https://wiki.bloodontheclocktower.com/Butcher",
    "https://wiki.bloodontheclocktower.com/Bone_Collector",
    "https://wiki.bloodontheclocktower.com/Harlot",
    "https://wiki.bloodontheclocktower.com/Barista",
    "https://wiki.bloodontheclocktower.com/Deviant",
    "https://wiki.bloodontheclocktower.com/Apprentice",
    "https://wiki.bloodontheclocktower.com/Matron",
    "https://wiki.bloodontheclocktower.com/Voudon",
    "https://wiki.bloodontheclocktower.com/Judge",
    "https://wiki.bloodontheclocktower.com/Bishop",
    "https://wiki.bloodontheclocktower.com/Cacklejack",
    "https://wiki.bloodontheclocktower.com/Gangster",
    "https://wiki.bloodontheclocktower.com/Gnome",
]
FABLED_CHARACTERS = [
    "https://wiki.bloodontheclocktower.com/Doomsayer",
    "https://wiki.bloodontheclocktower.com/Angel",
    "https://wiki.bloodontheclocktower.com/Buddhist",
    "https://wiki.bloodontheclocktower.com/Hell%27s_Librarian",
    "https://wiki.bloodontheclocktower.com/Revolutionary",
    "https://wiki.bloodontheclocktower.com/Fiddler",
    "https://wiki.bloodontheclocktower.com/Toymaker",
    "https://wiki.bloodontheclocktower.com/Fibbin",
    "https://wiki.bloodontheclocktower.com/Duchess",
    "https://wiki.bloodontheclocktower.com/Sentinel",
    "https://wiki.bloodontheclocktower.com/Spirit_of_Ivory",
    "https://wiki.bloodontheclocktower.com/Djinn",
    "https://wiki.bloodontheclocktower.com/Bootlegger",
    "https://wiki.bloodontheclocktower.com/Deus_ex_Fiasco",
    "https://wiki.bloodontheclocktower.com/Ferryman",
    "https://wiki.bloodontheclocktower.com/Gardener",
    "https://wiki.bloodontheclocktower.com/Storm_Catcher",
]


def with_category(links: list[str], category: str):
    return [(i, category) for i in links]


ALL_CHARACTERS = [
    *with_category(EXPERIMENTAL_CHARACTERS, "experimental"),
    *with_category(TROUBLE_BREWING_CHARACTERS, "trouble brewing"),
    *with_category(SECTS_AND_VIOLETS_CHARACTERS, "sects and violets"),
    *with_category(BAD_MOON_RISING_CHARACTERS, "bad moon rising"),
    *with_category(TRAVELLER_CHARACTERS, "travellers"),
    *with_category(FABLED_CHARACTERS, "fabled"),
]

for character, script in ALL_CHARACTERS:
    print(character)

    name = character.split("/")[-1]
    # if os.path.exists(f"characters/{name}.json"):
    #     with open(f"characters/{name}.json") as f:
    #         t = json.load(f)
    #         if "script" in t and "groups" in t and t["groups"]:
    #             continue

    response = requests.get(character)
    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.select_one("span.mw-page-title-main").get_text(strip=True)

    groups = [i.get_text().strip() for i in soup.select(".catlinks ul li a")]

    tagline_element = soup.find(
        lambda k: "flavour" not in k.get("class", []) and k.get_text().startswith('"')
    )
    tagline = tagline_element.get_text(strip=True).strip('"')

    # break

    image_tag = soup.select_one("#character-details a img")
    image_url = image_tag["src"] if image_tag else None

    # Download the image and save it to the images folder
    if image_url:
        image_name = os.path.join("images", os.path.basename(title + ".png"))

        if not os.path.exists(image_name):
            image_response = requests.get(
                "https://wiki.bloodontheclocktower.com" + image_url
            )
            with open(image_name, "wb") as img_file:
                img_file.write(image_response.content)
    else:
        image_name = None

    # Create the character info dictionary
    character_info = {
        "name": title,
        "description": tagline,
        "image": image_name,
        "groups": groups,
        "script": script,
    }

    # Save the character info to a JSON file
    json_file_path = os.path.join("characters", f"{title}.json")
    with open(json_file_path, "w") as json_file:
        json.dump(character_info, json_file, indent=4)

    print(f"Character info saved to {json_file_path}")

    time.sleep(random.random() + 0.5)
