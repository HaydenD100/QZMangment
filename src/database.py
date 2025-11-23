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
    CREATE TABLE IF NOT EXISTS "User" (
        ID SERIAL PRIMARY KEY,
        Name VARCHAR(150) NOT NULL,
        HashedPassword VARCHAR(255) NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS "Software" (
        ID SERIAL PRIMARY KEY,
        Name VARCHAR(150) NOT NULL,
        CVSS NUMERIC(4,2),
        Summary TEXT,
        Recommendation TEXT,
        LastScan TIMESTAMP,
        UserID INT,
        FOREIGN KEY (UserID) REFERENCES "User"(ID) ON DELETE SET NULL
    );
    """)
    
    cur.execute("INSERT INTO \"User\" (Name, HashedPassword) VALUES (%s, %s);", ("test", "test1"))

    conn.commit()

def AddUser(name, hashedpassword):
    global conn, cur
    cur.execute("INSERT INTO \"User\" (Name, HashedPassword) VALUES (%s, %s);", (name, hashedpassword))
    conn.commit()

def GetUser(name):
    global conn, cur
    cur.execute('SELECT ID, Name, HashedPassword FROM "User" WHERE Name = %s;', (name,))
    user_row = cur.fetchone() 
    if user_row:
        userClass = User() 
        userClass.ID = user_row[0]
        userClass.Name = user_row[1]
        userClass.HashedPassword = user_row[2]
    else:
        userClass = None
    return userClass

def AddSoftware(UserName, SoftwareName, CVSS=None, Summary=None, Recommendation=None, LastScan=None):
    global conn, cur
    cur.execute('SELECT ID FROM "User" WHERE Name = %s;', (UserName,))
    row = cur.fetchone()
    if not row:
        print(f"User '{UserName}' not found.")
        return None
    user_id = row[0]
    cur.execute("""
        INSERT INTO "Software" (Name, CVSS, Summary, Recommendation, LastScan, UserID)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING ID;
    """, (SoftwareName, CVSS, Summary, Recommendation, LastScan, user_id))
    software_id = cur.fetchone()[0]
    conn.commit()
    print(f"Inserted Software '{SoftwareName}' with ID {software_id} for User '{UserName}'")
    return software_id

def GetSoftwareByUser(UserName):
    global cur
    cur.execute('SELECT ID FROM "User" WHERE Name = %s;', (UserName,))
    row = cur.fetchone()
    if not row:
        print(f"User '{UserName}' not found.")
        return []

    user_id = row[0]

    cur.execute("""
        SELECT ID, Name, CVSS, Summary, Recommendation, LastScan, UserID
        FROM "Software"
        WHERE UserID = %s;
    """, (user_id,))

    rows = cur.fetchall()
    software_list = []
    for r in rows:
        sw = Software()
        sw.ID = r[0]
        sw.Name = r[1]
        sw.CVSS = r[2]
        sw.Summary = r[3]
        sw.Recommendation = r[4]
        sw.LastScan = r[5]
        sw.UserID = r[6]
        software_list.append(sw)

    return software_list

def UpdateSoftwareByID(SoftwareID, Name=None, CVSS=None, Summary=None, Recommendation=None, LastScan=None):
    global conn, cur
    fields = []
    values = []

    if Name is not None:
        fields.append("Name = %s")
        values.append(Name)
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


InitDataBase()
user = GetUser("test")
print(user.Name)


