import requests
from bs4 import BeautifulSoup

page = requests.get("https://callofduty.fandom.com/wiki/Template:CoD9_Weapons")
soup = BeautifulSoup(page.content, "html.parser")
content = soup.find(id="content")
table = content.find_all("table")[1]
tr = table.find_all("tr")

to_write = ["""DROP TABLE IF EXISTS CLASS;

CREATE TABLE CLASS
(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name VARCHAR(30),
    Attachment INTEGER,
        FOREIGN KEY (Attachment) REFERENCES ATTACHMENTForClass(AttachmentID)
);

DROP TABLE IF EXISTS GUN;

CREATE TABLE GUN
(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name VARCHAR(30),
    Damage VARCHAR(16),
    Class INTEGER References Class(ID),
    MagSize VARCHAR(16),
    FireMode VarChar(16)
);

DROP TABLE IF EXISTS Attachment;

CREATE TABLE Attachment
(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name VARCHAR(16),
    Class INTEGER References AttachmentForClass(ClassID)
);

DROP TABLE IF EXISTS AttachmentForClass;

CREATE TABLE AttachmentForClass
(
    ClassID INTEGER References Class(ID),
    AttachmentID INTEGER References Attachment(ID),
    PRIMARY KEY (ClassID, AttachmentID)
);
    """]

to_get = []

for i, l in enumerate(tr):
    if (i+1) % 2 and i != 0:
        if list(l.stripped_strings)[0] == "Access Kit":
            break
        to_write.append("INSERT INTO CLASS VALUES(null, '%s', 0);\n" %
                        str(list(l.stripped_strings)[0][:-1]))
        test = list(l.stripped_strings)
        for item in test:
            if test[0] not in [item, []] and item[0] != '(' and len(item) != 1 and item != "Revolution DLC":
                to_get.append(item)


for item in to_get:
    noInfo = False
    page = requests.get("https://callofduty.fandom.com/wiki/%s" %
                        (item.replace(" ", "_")))
    soup = BeautifulSoup(page.content, "html.parser")
    asideElement = None
    asideElement = list(soup.find("aside").stripped_strings)
    # try:
    if not asideElement:
        page = requests.get(
            "https://callofduty.fandom.com/wiki/%s_(weapon)" % (item.replace(" ", "_")))
        soup = BeautifulSoup(
            page.content, "html.parser")
    # if item.replace("-", " ").lower() not in asideElement[0].replace("-", " ").lower():
    asideElements = soup.find_all("aside")
    for aside in asideElements:
        temp = list(aside.stripped_strings)
        if len(temp) < 1: continue
        for i, l in enumerate(tr):
            if i>1:

                if item in list(tr[18].stripped_strings):
                    # print("IT IS")
                    noInfo = True
                    break
        if (all(x in temp for x in [item, "Damage", "Weapon Class", "Magazine Size", "Fire Mode"]) or ("Colt M16A1" in temp or "Barrett M82A1" in temp)) and not noInfo:
            asideElement = list(aside.stripped_strings)
            break
    if noInfo: continue
    if len(asideElement) == 0: continue
    try:
        name = item
        
        damage = asideElement[asideElement.index(
            "Damage")+1].replace("–","-").replace("·","") if "Damage" in asideElement else 0
        if isinstance(damage, str):
            if not damage.split()[0].isnumeric():
                if damage.split()[1].isnumeric():
                    damage = damage.split()[1]
                damage = damage.split()[0].strip().removesuffix(":")
            

        if "Weapon Class" in asideElement:
            
            cls = asideElement[asideElement.index(
                "Weapon Class")+1].replace("–","-").replace("Handgun", "Pistol").removesuffix("s").title()
        else:
            cls = "Unknown"
        index = to_get.index(item)
        if index>=to_get.index("Frag Grenade"):
            cls = "Lethal"
        if index>=to_get.index("Smoke Grenade"):
            cls = "Tactical"
        
        if "Magazine Size" in asideElement:
            mag = asideElement[asideElement.index("Magazine Size")+1].replace("�","")
            mag = mag.split()
            if mag[0].isnumeric():
                mag = mag[0]
            else:
                mag = mag[1]
        else:
            mag = "Unknown"

        if "Fire Mode" in asideElement:
            fireMode = asideElement[asideElement.index(
                "Fire Mode")+1].replace("�","")
            if "burst" in fireMode.lower():
                fireMode = "Burst"
            elif "semi-automatic" in fireMode.lower():
                fireMode = "Semi-Automatic"
            elif "automatic" in fireMode.lower():
                fireMode = "Automatic"
        else:
            fireMode = "Unknown"

        to_write.append("INSERT INTO GUN VALUES( null, '%s', '%s', '%s', '%s', '%s' );\n" % (name,
                                                                                                damage,
                                                                                                cls,
                                                                                                mag,
                                                                                                fireMode,
                                                                                                ))
    except Exception as e:
        print(asideElement, e)
print(to_get)
print(len(to_get))
with open("createTables.sql", "w") as f:
    f.write("\n".join(to_write))
