import requests
import threading, time, sys, itertools
from bs4 import BeautifulSoup


def get_class(page:BeautifulSoup) -> str:
    return " ".join(list(page.stripped_strings))

def get_guns(page:BeautifulSoup) -> list:
    guns = list(page.next_sibling.stripped_strings)
    for _ in range(guns.count("·")):
        guns.remove('·')
    if "Revolution DLC" in guns:
        guns.remove("Revolution DLC")
    if ")" in guns:
        guns.remove(")")
    return format_guns(guns)

def get_info(cls:str, guns:list, gun:bool, classes:list = None) -> dict :
    if gun:
        gunReturn = {cls: dict()}
        for gun in guns:
            noInfo = False
            damage = 0
            mag = 0
            fireMode = "Unknown"
            # Get page
            url = "https://callofduty.fandom.com/wiki/%s" % gun.replace(" ","_")
            soup = BeautifulSoup(requests.get(url).text, "html.parser")
            # If the aside isn't there, try grab the *other* page if it exists
            if not len(soup.find_all("aside")) > 1 and cls != "Unobtainable Item":
                url = "https://callofduty.fandom.com/wiki/%s_(weapon)" % gun.replace(" ", "_")
                soup = BeautifulSoup(requests.get(url).text, "html.parser")

            # Get the header 2 - BO2:
            header = soup.find(id="Call_of_Duty:_Black_Ops_II")
            aside = None
            if not header:
                aside = list(soup.find("aside").stripped_strings)
            else:
                aside = list(soup.find(id="Call_of_Duty:_Black_Ops_II").parent.find_next("aside").stripped_strings)
                # Sometimes aside is before header
                if not aside:
                    aside = soup.find(id="Call_of_Duty:_Black_Ops_II").find_previous("aside")
                    if not aside:
                        noInfo = True
                    else:
                        aside = list(aside.stripped_strings)
            
            if not noInfo:
                # Get Damage
                damage = None

                if "Damage" in aside:
                    damage = aside[aside.index("Damage")+1].replace("–"," ").replace("-"," ").replace("/"," ").replace(",","").replace(":"," ")
                else: 
                    damage = 0
                # Grab specific section
                if isinstance(damage, str):
                    
                    # Remove any - such as 30-9
                    if "-" in damage:
                        damage = damage.split("-")[0]

                    # If the split provides multiple points e.g. ["Explosion:", "20"]
                    if gun == "Thrustodyne Aeronautics Model 23":
                        damage = damage.split()[0]
                    else:
                        if len(damage.split()) > 1:
                            if damage.split()[0].isnumeric():
                                damage = damage.split()[0]
                            elif damage.split()[1].isnumeric():
                                damage = damage.split()[1]
                        elif not damage.isnumeric():
                            damage = aside[aside.index("Damage")+2].replace("–"," ").replace("-"," ").split()[0]
                            if len(damage.split()) > 1:
                                if damage.split()[0].isnumeric():
                                    damage = damage.split()[0]
                                elif damage.split()[1].isnumeric():
                                    damage = damage.split()[1]
                if damage == '\u221e' or "infinite" in str(damage).lower():
                    damage = "9999"
                # if any(x in str(damage).lower() for x in ["medium", "low", "weapon","used","cost", "magazine"]):
                #     damage = 0
                damage = str(damage).replace('\u2248',"")
                damage = str(damage).replace(',',"")
                if not str(damage).isnumeric():
                    damage = 0

                # Get Mag Size
                mag = None
                if "Magazine Size" in aside:
                    mag = aside[aside.index("Magazine Size")+1].replace("–"," ")
                if isinstance(mag, str):
                    if "Zero" in mag or "None" in mag:
                        mag = 0
                else: 
                    mag = 0
                if "infinite" in str(mag).lower():
                    mag = 9999
                if "standard" in str(mag).lower():
                    mag = 0

                if isinstance(mag, str):
                    if len(mag.split()) > 1:
                        if (mag.split()[0].isnumeric() and mag.split()[0] != "·"):
                            mag = mag.split()[0]
                        else:
                            mag = mag.split()[1]

                # Get Fire Mode
                fireMode = None
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
                    
                else:
                    fireMode = "Unknown"
            else:
                damage = 0
                mag = 0
                fireMode = "Unknown"

            gunReturn[cls][gun] = {"damage": int(damage), "magazine": int(mag), "fireMode": fireMode }
        return gunReturn
    else:
        attachmentReturn = {cls: dict()}
        for attachment in guns:
            if guns.index(attachment) >= guns.index("Grenade Launcher"):
                continue
            # Get page
            url = "https://callofduty.fandom.com/wiki/%s" % attachment.replace(" ","_")
            soup = BeautifulSoup(requests.get(url).text, "html.parser")

            # Get the header 2 - BO2:
            header = soup.find(id="Call_of_Duty:_Black_Ops_II")
            aside = None
            if not header:
                aside = list(soup.find("aside").stripped_strings)
            else:
                aside = list(soup.find(id="Call_of_Duty:_Black_Ops_II").parent.find_next("aside").stripped_strings)
                # Sometimes aside is before header
                if not aside:
                    aside = soup.find(id="Call_of_Duty:_Black_Ops_II").find_previous("aside")
                    if not aside:
                        noInfo = True
                    else:
                        aside = list(aside.stripped_strings)
            available_classes = []
            for cls in classes:
                for item in aside:
                    if cls.lower() in item.lower():
                        if cls not in available_classes:
                            available_classes.append(cls.removesuffix("s"))
                    if "smg" in item.lower() or "submachine" in item.lower():
                        if not "Submachine Gun" in available_classes:
                            available_classes.append("Submachine Gun")
                    if "lmg" in item.lower():
                        if not "Light Machine Gun" in available_classes:
                            available_classes.append("Submachine Gun")
                    if "handgun" in item.lower():
                        if not "Pistol" in available_classes:
                            available_classes.append("Pistol")
            attachmentReturn["Attachment"][attachment] = {"name":attachment,"classes":list(set(available_classes))}
        return attachmentReturn

def format_guns(guns:list) -> list:
    for _ in range(guns.count("·")):
        guns.remove('·')
    for _ in range(guns.count(",")):
        guns.remove(',')
    for gun in guns:
        if any(x in gun for x in ["(",")",":"]):
            guns.pop(guns.index(gun))
    return guns

def get_attachments(page:BeautifulSoup) -> list:
    attachments = list(page.next_sibling.stripped_strings)

    return attachments

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

page = requests.get("https://callofduty.fandom.com/wiki/Template:CoD9_Weapons")

soup = BeautifulSoup(page.content,"html.parser")

divs = soup.find_all("td", {"class": "navbox-group"})

classes = []
for c in divs:
    cls = get_class(c)
    if cls != "Miscellaneous":
        cls = cls.removesuffix("s")
    classes.append(cls)
for i, cls in enumerate(classes):
    if cls != "Miscellaneous":
        cls = cls.removesuffix("s")
    if cls == "Access Kit Item":
        continue

    to_write.append("\nINSERT INTO CLASS VALUES(null, \"%s\");\n" % cls)
    if not cls == "Attachment":
        guns = get_info(cls, get_guns(divs[i]), True)
        for gun in guns[cls]:
            to_write.append("INSERT INTO WEAPON VALUES(null, \"%s\", %s, %s, %s, \"%s\");" %(gun, guns[cls][gun]["damage"],i+1 if i<11 else i,guns[cls][gun]["magazine"],guns[cls][gun]["fireMode"]))
    else:
        if cls != "Cut":
            attachment_list = get_attachments(divs[i])
            attach_list = []
            for i, attach in enumerate(attachment_list):
                if not any(x in attach for x in ["·","(",")",","]):
                    attach_list.append(attach)
            attachment_list = attach_list
            attachments = get_info(cls, attachment_list, False, classes)
            for attachment in attachments[cls]:
                to_write.append("INSERT INTO ATTACHMENT VALUES(null, \"%s\");\n" %(attachment))
                for class_ in attachments[cls][attachment]["classes"]:
                    to_write.append("INSERT INTO ATTACHMENTFORCLASS VALUES(%s, %s);\n" %(classes.index(class_)+1, attachment_list.index(attachment)+1))

with open("createTables.sql",'w') as f:
    f.write("\n".join(to_write))

done = True