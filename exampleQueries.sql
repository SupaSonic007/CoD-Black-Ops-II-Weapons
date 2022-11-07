-- See all information of each weapon
SELECT * FROM WEAPON;

-- See attachments for Shotguns
SELECT a.Name as 'Attachment', c.Name as 'Class'
FROM ATTACHMENT a
JOIN ATTACHMENTFORCLASS ac ON a.ID == ac.AttachmentID
JOIN CLASS c ON ac.ClassID == c.ID
WHERE c.Name == 'Shotgun'
ORDER BY c.ID, a.ID ASC;

-- See each weapon's class
SELECT w.Name as 'Weapon', c.Name as 'Class'
FROM WEAPON w
JOIN CLASS c ON c.ID == w.Class;

-- Grab snipers and their respective damages
SELECT w.Name as 'Weapon', w.Damage
FROM WEAPON w
JOIN Class c on c.ID == w.Class
where c.Name == 'Sniper Rifle';

-- All tables combined and sorted by weapon
SELECT * 
FROM WEAPON w
JOIN CLASS c ON c.ID = w.Class
JOIN ATTACHMENTFORCLASS ac ON ac.ClassID == c.ID
JOIN ATTACHMENT a ON ac.AttachmentID == a.ID
WHERE ac.ClassID == c.ID
ORDER BY w.ID ASC;

-- Grab classes and attachments
SELECT c.Name as 'Class', a.Name as 'Attachment'
FROM CLASS c, ATTACHMENT a, ATTACHMENTFORCLASS ac
WHERE ac.ClassID == c.ID and ac.AttachmentID == a.ID
ORDER BY c.ID ASC;

-- Grab all weapons that can use Fast Mag
SELECT w.Name, a.Name
FROM WEAPON w, ATTACHMENT a, Class c, ATTACHMENTFORCLASS ac
WHERE a.ID == ac.AttachmentID and ac.ClassID == c.ID and w.Class == c.ID and a.Name == "Fast Mag";

-- Wonder Weapons from Zombies
Select w.Name, w.Damage
FROM WEAPON w, CLASS c
WHERE w.Class = c.ID and c.Name == "Wonder Weapon";

-- All Attachments
Select *
FROM ATTACHMENT;