import psycopg
from common import *

conn = None
cur = None

def InitDataBase():
    global conn, cur
    conn = psycopg.connect(
        dbname="Monitor",
        user="postgres",
        password="admin123",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS "UserMonitor" (
        ID SERIAL PRIMARY KEY,
        Name VARCHAR(150) NOT NULL UNIQUE,
        HashedPassword VARCHAR(255) NOT NULL,
        OS VARCHAR(255),
        Build VARCHAR(255)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS "Software" (
    ID SERIAL PRIMARY KEY,
    Version VARCHAR(255),
    Name VARCHAR(150) NOT NULL,
    CVSS NUMERIC(4,2),
    Summary TEXT,
    Recommendation TEXT,
    LastScan TIMESTAMP,
    UserID INT,
    FOREIGN KEY (UserID) REFERENCES "UserMonitor"(ID) ON DELETE SET NULL,
    CONSTRAINT unique_user_software UNIQUE (Name, UserID)
    );
    """)

    cur.execute("INSERT INTO \"UserMonitor\" (Name, HashedPassword) VALUES (%s, %s) ON CONFLICT (Name) DO NOTHING;", ("test", "test1"))
    cur.execute("INSERT INTO \"UserMonitor\" (Name, HashedPassword) VALUES (%s, %s) ON CONFLICT (Name) DO NOTHING;", ("test@qz.com", "test1"))
    cur.execute("INSERT INTO \"UserMonitor\" (Name, HashedPassword) VALUES (%s, %s) ON CONFLICT (Name) DO NOTHING;", ("admin@qz.com", "admin123"))

    conn.commit()

def AddUser(name, hashedpassword):
    global conn, cur
    cur.execute("INSERT INTO \"UserMonitor\" (Name, HashedPassword) VALUES (%s, %s) ON CONFLICT (Name) DO NOTHING;", (name, hashedpassword))
    conn.commit()

def UpdateUser(name, OS = None, BuildVersion = None):
    cur.execute("""
    UPDATE "UserMonitor"
    SET OS = %s,
        Build = %s
    WHERE Name = %s;
    """, (OS, BuildVersion, name))

def GetUser(name):
    global conn, cur
    cur.execute('SELECT ID, Name, HashedPassword FROM "UserMonitor" WHERE Name = %s;', (name,))
    user_row = cur.fetchone() 
    if user_row:
        userClass = User() 
        userClass.ID = user_row[0]
        userClass.Name = user_row[1]
        userClass.HashedPassword = user_row[2]
    else:
        userClass = None
    return userClass

def AddSoftware(UserName, SoftwareName, Version, CVSS=None, Summary=None, Recommendation=None, LastScan=None):
    global conn, cur
    cur.execute('SELECT ID FROM "UserMonitor" WHERE Name = %s;', (UserName,))
    row = cur.fetchone()
    if not row:
        print(f"User '{UserName}' not found.")
        return None
    user_id = row[0]
    cur.execute("""
        INSERT INTO "Software" (Name,Version, CVSS, Summary, Recommendation, LastScan, UserID)
        VALUES (%s,%s, %s, %s, %s, %s, %s)
        RETURNING ID;
    """, (SoftwareName,Version, CVSS, Summary, Recommendation, LastScan, user_id))
    software_id = cur.fetchone()[0]
    conn.commit()
    print(f"Inserted Software '{SoftwareName}' with ID {software_id} for UserMonitor '{UserName}'")
    return software_id

def GetAllSoftware():
    cur.execute('SELECT * FROM "Software";')
    rows = cur.fetchall()
    software_list = []
    for r in rows:
        sw = Software()
        print(r)
        sw.ID = r[0]
        sw.Name = r[2]       # Should be 'version' here
        sw.Version = r[1]    # Should be 'name' here
        sw.CVSS = r[3]
        sw.Summary = r[4]
        sw.Recommendation = r[5]
        sw.LastScan = r[6]
        sw.UserID = r[7]
        software_list.append(sw)

    return software_list

def GetSoftwareByUser(UserName):
    global cur
    cur.execute('SELECT ID FROM "UserMonitor" WHERE Name = %s;', (UserName,))
    row = cur.fetchone()
    if not row:
        print(f"User '{UserName}' not found.")
        return []

    user_id = row[0]

    cur.execute("""
        SELECT *
        FROM "Software"
        WHERE UserID = %s;
    """, (user_id,))

    rows = cur.fetchall()
    software_list = []
    for r in rows:
        sw = Software()
        sw.ID = r[0]
        sw.Name = r[1]       # Should be 'version' here
        sw.Version = r[2]    # Should be 'name' here
        sw.CVSS = r[3]
        sw.Summary = r[4]
        sw.Recommendation = r[5]
        sw.LastScan = r[6]
        sw.UserID = r[7]
        software_list.append(sw)

    return software_list

def GetSoftwareByUser(UserName, SoftwareName):
    global cur
    cur.execute('SELECT ID FROM "UserMonitor" WHERE Name = %s;', (UserName,))
    row = cur.fetchone()
    if not row:
        print(f"User '{UserName}' not found.")
        return []

    user_id = row[0]

    cur.execute("""
        SELECT *
        FROM "Software"
        WHERE UserID = %s AND Name = %s;
    """, (user_id,SoftwareName))

    r = cur.fetchall()
    r = r[0]
    sw = Software()
    sw.ID = r[0]
    sw.Name = r[1]       # Should be 'version' here
    sw.Version = r[2]    # Should be 'name' here
    sw.CVSS = r[3]
    sw.Summary = r[4]
    sw.Recommendation = r[5]
    sw.LastScan = r[6]
    sw.UserID = r[7]       

    return sw

def UpdateSoftwareByID(SoftwareID, Name=None, Version=None, CVSS=None, Summary=None, Recommendation=None, LastScan=None):
    global conn, cur
    fields = []
    values = []

    if Name is not None:
        fields.append("Name = %s")
        values.append(Name)
    if Version is not None:
        fields.append("Version = %s")
        values.append(Version)
    if CVSS is not None:
        fields.append("CVSS = %s")
        values.append(CVSS)
    if Summary is not None:
        fields.append("Summary = %s")
        values.append(Summary)
    if Recommendation is not None:
        fields.append("Recommendation = %s")
        values.append(Recommendation)
    if LastScan is not None:
        fields.append("LastScan = %s")
        values.append(LastScan)

    if not fields:
        print("No fields to update.")
        return False

    values.append(SoftwareID) 

    sql = f"""
        UPDATE "Software"
        SET {', '.join(fields)}
        WHERE ID = %s;
    """

    cur.execute(sql, tuple(values))
    conn.commit()

    print(f"Software with ID {SoftwareID} updated successfully.")
    return True

def serialize_user(user):
    if not user:
        return None
    return {
        "ID": user.ID,
        "Name": user.Name,
        "HashedPassword": user.HashedPassword
    }

def serialize_software(s):
    return {
        "ID": s.ID,
        "Name": s.Name,
        "CVSS": s.CVSS,
        "Summary": s.Summary,
        "Recommendation": s.Recommendation,
        "LastScan": s.LastScan,
        "UserID": s.UserID,
        "Version": s.Version
    }

InitDataBase()