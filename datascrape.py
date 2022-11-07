import requests
import threading
import time
import sys
import itertools
from bs4 import BeautifulSoup


def get_class(page: BeautifulSoup) -> str:
    # Return the list of stripped strings (or the class name) at the specified point of the page
    return " ".join(list(page.stripped_strings))


def get_guns(page: BeautifulSoup) -> list:
    # For each gun, get the gun name
    # Page has the position of the class name, next to it is the list of weapons
    guns = list(page.next_sibling.stripped_strings)
    # Remove parts that don't fit
    for _ in range(guns.count("·")):
        guns.remove('·')
    if "Revolution DLC" in guns:
        guns.remove("Revolution DLC")
    if ")" in guns:
        guns.remove(")")
    # Return a formatted version of the guns
    return format_guns(guns)


def get_info(cls: str, guns: list, gun: bool, classes: list = None) -> dict:
    # Get info for guns or attachments
    if gun:
        # Retun a dictionary for the class with each gun and associated info
        gunReturn = {cls: dict()}
        # If the gun has no info, it won't try to find the info from the page
        for gun in guns:
            noInfo = False
            damage = 0
            mag = 0
            fireMode = "Unknown"
            # Get page
            url = "https://callofduty.fandom.com/wiki/%s" % gun.replace(
                " ", "_")
            soup = BeautifulSoup(requests.get(url).text, "html.parser")
            # If the aside element isn't there, try grab the *other* page if it exists
            # There will always be 2 or more if it is the correct page, as one is for showing other pages
            if not len(soup.find_all("aside")) > 1 and cls != "Unobtainable Item":
                url = "https://callofduty.fandom.com/wiki/%s_(weapon)" % gun.replace(
                    " ", "_")
                soup = BeautifulSoup(requests.get(url).text, "html.parser")

            # Get the h2:
            header = soup.find(id="Call_of_Duty:_Black_Ops_II")
            # init aside
            aside = None
            # If there was not a h2 try finding the aside element not to do with the aside
            if not header:
                aside = list(soup.find("aside").stripped_strings)
            # If there was, find the aside that was after the h2
            else:
                aside = list(soup.find(id="Call_of_Duty:_Black_Ops_II").parent.find_next(
                    "aside").stripped_strings)
                # Sometimes the aside is before header
                if not aside:
                    aside = soup.find(
                        id="Call_of_Duty:_Black_Ops_II").find_previous("aside")
                    # If it cannot find the aside, there is no info and don't try to find new info
                    if not aside:
                        noInfo = True
                    # otherwise grab the aside element
                    else:
                        aside = list(aside.stripped_strings)

            if not noInfo:
                # Get Damage
                damage = None

                # If the info is there, grab it, otherwise it will be 0
                if "Damage" in aside:
                    damage = aside[aside.index("Damage")+1].replace("–", " ").replace(
                        "-", " ").replace("/", " ").replace(",", "").replace(":", " ")
                else:
                    damage = 0

                # No formatting if it is
                if isinstance(damage, str):

                    # Remove any - such as 30-9
                    if "-" in damage:
                        damage = damage.split("-")[0]

                    # If the split provides multiple points e.g. ["Explosion:", "20"]
                    # This specific gun causes issues, manually grab the info
                    if gun == "Thrustodyne Aeronautics Model 23":
                        damage = damage.split()[0]
                    else:
                        # If it can be split, check whether each section is a number, if not select the other one
                        if len(damage.split()) > 1:
                            if damage.split()[0].isnumeric():
                                damage = damage.split()[0]
                            elif damage.split()[1].isnumeric():
                                damage = damage.split()[1]
                        # If it can't be split, and it isn't a number, I'm probably 1 element too early, go to the next one and try again
                        elif not damage.isnumeric():
                            damage = aside[aside.index(
                                "Damage")+2].replace("–", " ").replace("-", " ").split()[0]
                            if len(damage.split()) > 1:
                                if damage.split()[0].isnumeric():
                                    damage = damage.split()[0]
                                elif damage.split()[1].isnumeric():
                                    damage = damage.split()[1]
                # Infinity symbol or infinite will be replaced by 9999
                if damage == '\u221e' or "infinite" in str(damage).lower():
                    damage = "9999"

                # Format to work correctly
                damage = str(damage).replace('\u2248', "")
                damage = str(damage).replace(',', "")

                # Make sure it's a number, otherwise reset it
                if not str(damage).isnumeric():
                    damage = 0

                # Get Mag Size
                mag = None
                # Grab mag size if it exists
                if "Magazine Size" in aside:
                    mag = aside[aside.index(
                        "Magazine Size")+1].replace("–", " ")

                # If it's zero or non-existent it will reset to 0
                if isinstance(mag, str):
                    if "Zero" in mag or "None" in mag:
                        mag = 0
                else:
                    mag = 0
                # Infinite = 9999 for this case as it's large enough
                if "infinite" in str(mag).lower():
                    mag = 9999
                # Remove anything that makes no sense and reset
                if "standard" in str(mag).lower():
                    mag = 0

                # Run the same checks as damage
                if isinstance(mag, str):
                    if len(mag.split()) > 1:
                        if (mag.split()[0].isnumeric() and mag.split()[0] != "·"):
                            mag = mag.split()[0]
                        else:
                            mag = mag.split()[1]

                # Get Fire Mode
                fireMode = None
                # Re-format fire mode and make it consistent
                if "Fire Mode" in aside:
                    fireMode = aside[aside.index("Fire Mode")+1]
                    if "burst" in fireMode.lower():
                        fireMode = "Burst"
                    elif "semi" in fireMode.lower():
                        fireMode = "Semi-Automatic"
                    elif "auto" in fireMode.lower():
                        fireMode = "Automatic"
                    elif "bolt" in fireMode.lower():
                        fireMode = "Bolt-Action"
                    elif "melee" in fireMode.lower():
                        fireMode = "Melee"
                    elif "single" in fireMode.lower():
                        fireMode = "Single-Shot"
                # If it doesn't exist, reset to Unknown
                else:
                    fireMode = "Unknown"
            # If no info, reset variables
            else:
                damage = 0
                mag = 0
                fireMode = "Unknown"

            # Update return info
            gunReturn[cls][gun] = {"damage": int(
                damage), "magazine": int(mag), "fireMode": fireMode}
        return gunReturn
    else:
        # Return a dictionary of attachments
        attachmentReturn = {cls: dict()}
        # It's called guns still, don't judge
        for attachment in guns:
            # IF I don't want it, remove it
            if guns.index(attachment) >= guns.index("Grenade Launcher"):
                continue
            # Get page
            url = "https://callofduty.fandom.com/wiki/%s" % attachment.replace(
                " ", "_")
            soup = BeautifulSoup(requests.get(url).text, "html.parser")

            # Get the h2:
            header = soup.find(id="Call_of_Duty:_Black_Ops_II")
            aside = None
            # Grab the info like with the weapons
            # Refer to the previous comments in weapons
            if not header:
                aside = list(soup.find("aside").stripped_strings)
            else:
                aside = list(soup.find(id="Call_of_Duty:_Black_Ops_II").parent.find_next(
                    "aside").stripped_strings)
                # Sometimes aside is before header
                if not aside:
                    aside = soup.find(
                        id="Call_of_Duty:_Black_Ops_II").find_previous("aside")
                    if not aside:
                        noInfo = True
                    else:
                        aside = list(aside.stripped_strings)

            # Init available classes list for the attachment
            available_classes = []
            for cls in classes:
                # For each class
                for item in aside:
                    # For each attachment
                    if cls.lower() in item.lower():
                        # If the class is mentioned in the string, add it to the list and remove the "s" at the end because it doesn't belong there
                        if cls not in available_classes:
                            available_classes.append(cls.removesuffix("s"))

                    # Check for any other variants of the names
                    if "smg" in item.lower() or "submachine" in item.lower():
                        if not "Submachine Gun" in available_classes:
                            available_classes.append("Submachine Gun")
                    if "lmg" in item.lower():
                        if not "Light Machine Gun" in available_classes:
                            available_classes.append("Submachine Gun")
                    if "handgun" in item.lower():
                        if not "Pistol" in available_classes:
                            available_classes.append("Pistol")

            #  Add the attachment and info to the return
            attachmentReturn["Attachment"][attachment] = {
                "name": attachment, "classes": list(set(available_classes))}
        return attachmentReturn


def format_guns(guns: list) -> list:
    # Format the list, have no "·", ",", "(", ")", ":"
    for _ in range(guns.count("·")):
        guns.remove('·')
    for _ in range(guns.count(",")):
        guns.remove(',')
    for gun in guns:
        if any(x in gun for x in ["(", ")", ":"]):
            guns.pop(guns.index(gun))
    return guns


def get_attachments(page: BeautifulSoup) -> list:
    # Get each attachment from the category
    attachments = list(page.next_sibling.stripped_strings)

    return attachments

# What to write in the sql file
to_write = ["""DROP TABLE IF EXISTS CLASS;

CREATE TABLE CLASS
(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name VARCHAR(30)
);

DROP TABLE IF EXISTS WEAPON;

CREATE TABLE WEAPON
(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name VARCHAR(30),
    Damage VARCHAR(16),
    Class INTEGER References Class(ID),
    MagSize VARCHAR(16),
    FireMode VarChar(16)
);

DROP TABLE IF EXISTS ATTACHMENT;

CREATE TABLE ATTACHMENT
(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name VARCHAR(16)
);

DROP TABLE IF EXISTS ATTACHMENTFORCLASS;

CREATE TABLE ATTACHMENTFORCLASS
(
    ClassID INTEGER References Class(ID),
    AttachmentID INTEGER References Attachment(ID),
    PRIMARY KEY (ClassID, AttachmentID)
);
"""]

done = False
# Animation from https://stackoverflow.com/questions/22029562/python-how-to-make-simple-animated-loading-while-process-is-running

# Cool loading animation
def animate():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write('\rScraping... ' + c)
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rDone!     ')


t = threading.Thread(target=animate)
t.start()

# Grab the weapons page
page = requests.get("https://callofduty.fandom.com/wiki/Template:CoD9_Weapons")

# Parse the html
soup = BeautifulSoup(page.content, "html.parser")

# Grab all of the groups
divs = soup.find_all("td", {"class": "navbox-group"})

# Grab all of the classes and chuck them in a list without the "s" suffix (except for Miscellaneous)
classes = []
for c in divs:
    cls = get_class(c)
    if cls != "Miscellaneous":
        cls = cls.removesuffix("s")
    classes.append(cls)

# Grab the index and class for each class
for i, cls in enumerate(classes):
    if cls != "Miscellaneous":
        cls = cls.removesuffix("s")
    if cls == "Access Kit Item":
        continue
    
    # Insert class into db
    to_write.append("\nINSERT INTO CLASS VALUES(null, \"%s\");\n" % cls)
    if not cls == "Attachment":
        # Grab the dictionary of all weapons with info
        guns = get_info(cls, get_guns(divs[i]), True)
        # For each gun (name)
        for gun in guns[cls]:
            # Insert weapon into db with values
            # the i+1 if i<11 else i represents the skipped class and fixes an offset of the class IDs
            to_write.append("INSERT INTO WEAPON VALUES(null, \"%s\", %s, %s, %s, \"%s\");" % (
                gun, guns[cls][gun]["damage"], i+1 if i < 11 else i, guns[cls][gun]["magazine"], guns[cls][gun]["fireMode"]))
    else:
        # For some reason the Cut class was an issue
        if cls != "Cut":
            # Grab all attachments
            attachment_list = get_attachments(divs[i])
            attach_list = []
            # Format attachments, removing anything painful
            for i, attach in enumerate(attachment_list):
                if not any(x in attach for x in ["·", "(", ")", ","]):
                    attach_list.append(attach)
            # Grab attachments from fixed attachment list
            attachment_list = attach_list
            attachments = get_info(cls, attachment_list, False, classes)
            # For attachment (name) in dict
            for attachment in attachments[cls]:
                # Insert the attachment into the db
                to_write.append(
                    "INSERT INTO ATTACHMENT VALUES(null, \"%s\");\n" % (attachment))
                #  For each class that it is applicable to
                for class_ in attachments[cls][attachment]["classes"]:
                    # Insert the relationship into the database
                    to_write.append("INSERT INTO ATTACHMENTFORCLASS VALUES(%s, %s);\n" % (
                        classes.index(class_)+1, attachment_list.index(attachment)+1))

# Write the new file to createTables.sql
with open("createTables.sql", 'w') as f:
    f.write("\n".join(to_write))

# Stop the animation
done = True
