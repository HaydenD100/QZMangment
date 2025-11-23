import psycopg
import json
import time
import google.generativeai as genai
from common import *

# --- CONFIGURATION ---
<<<<<<< HEAD
GEMINI_API_KEY = 'AIzaSyCGneEgup3QMbbXe6vaN8EFfvshBQDaPkQ' # <--- PASTE YOUR KEY HERE
=======
GEMINI_API_KEY = 'YOUR_GEMINI_KEY_HERE' # <--- PASTE YOUR KEY HERE
>>>>>>> 790b354eccc883528ae291808e703a7047a74624
BATCH_SIZE = 40

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
# We use the specific -001 version to avoid the 404 error
<<<<<<< HEAD
model = genai.GenerativeModel('gemini-2.5-flash')
=======
model = genai.GenerativeModel('gemini-1.5-flash-001')
>>>>>>> 790b354eccc883528ae291808e703a7047a74624

conn = None
cur = None

def InitDataBase():
    global conn, cur
    try:
        conn = psycopg.connect(
            dbname="Monitor",
            user="postgres",
            password="admin123",
            host="localhost",
            port="5432",
            connect_timeout=5 # <--- ADDED: Fails after 5s instead of hanging forever
        )
        cur = conn.cursor()
        print("[+] Database Connected.")
    except Exception as e:
        print(f"[!] Database Connection Failed: {e}")
        # We don't exit here so that imports don't crash the whole app, 
        # but the app won't work without DB.

    # --- TABLE CREATION ---
    if cur:
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
<<<<<<< HEAD
            CVSS VARCHAR(255),
=======
            CVSS NUMERIC(4,2),
>>>>>>> 790b354eccc883528ae291808e703a7047a74624
            Summary TEXT,
            Recommendation TEXT,
            LastScan TIMESTAMP,
            UserID INT,
            FOREIGN KEY (UserID) REFERENCES "UserMonitor"(ID) ON DELETE SET NULL,
            CONSTRAINT unique_user_software UNIQUE (Name, UserID)
        );
        """)
        
        # Default Users
        cur.execute("INSERT INTO \"UserMonitor\" (Name, HashedPassword) VALUES (%s, %s) ON CONFLICT (Name) DO NOTHING;", ("test", "test1"))
        cur.execute("INSERT INTO \"UserMonitor\" (Name, HashedPassword) VALUES (%s, %s) ON CONFLICT (Name) DO NOTHING;", ("test@qz.com", "test1"))
        cur.execute("INSERT INTO \"UserMonitor\" (Name, HashedPassword) VALUES (%s, %s) ON CONFLICT (Name) DO NOTHING;", ("admin@qz.com", "admin123"))

        conn.commit()

# --- CRUD FUNCTIONS ---

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
        VALUES (%s,%s, %s, %s, %s, %s, %s) ON CONFLICT (Name, UserID) DO NOTHING
    RETURNING ID;
    """, (SoftwareName,Version, CVSS, Summary, Recommendation, LastScan, user_id))
    
    # Check if insert actually happened (it might return None on conflict)
    res = cur.fetchone()
    if res:
        software_id = res[0]
        conn.commit()
        print(f"Inserted Software '{SoftwareName}' with ID {software_id} for UserMonitor '{UserName}'")
        return software_id
    else:
        return None

def GetAllSoftware():
    cur.execute('SELECT * FROM "Software";')
    rows = cur.fetchall()
    software_list = []
    for r in rows:
        sw = Software()
        # Note: Keeping your existing column mapping logic
        sw.ID = r[0]
        sw.Name = r[2]       # Assuming Name is column 2
        sw.Version = r[1]    # Assuming Version is column 1
        sw.CVSS = r[3]
        sw.Summary = r[4]
        sw.Recommendation = r[5]
        sw.LastScan = r[6]
        sw.UserID = r[7]
        software_list.append(sw)

    return software_list

def GetSoftwareByID(software_id):
    global cur
    # Get Software
    cur.execute("""
        SELECT *
        FROM "Software"
        WHERE ID = %s;
    """, (software_id,))
    r = cur.fetchone()
    if not r:
        return None 

    sw = Software()
    sw.ID = r[0]
    sw.Name = r[2]       # Correct field
    sw.Version = r[1]    # Correct field
    sw.CVSS = r[3]
    sw.Summary = r[4]
    sw.Recommendation = r[5]
    sw.LastScan = r[6]
    sw.UserID = r[7]

    return sw  # always a list
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
        sw.Name = r[1]       
        sw.Version = r[2]    
        sw.CVSS = r[3]
        sw.Summary = r[4]
        sw.Recommendation = r[5]
        sw.LastScan = r[6]
        sw.UserID = r[7]
        software_list.append(sw)

    return software_list

def GetSoftwareByUserAndName(UserName, SoftwareName):
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

    rows = cur.fetchall()
    if not rows: return None
    
    r = rows[0]
    sw = Software()
    sw.ID = r[0]
    sw.Name = r[1]       
    sw.Version = r[2]    
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

# --- AI CLEANING FUNCTIONS (NEW) ---

def CleanSoftwareNames():
    """
    Batches software names, sends them to Gemini for cleaning, and updates DB.
    Call this function manually when you want to clean your data.
    """
    print("[*] Starting AI Name Cleaning...")
    
    # Get all software
    cur.execute('SELECT ID, Name FROM "Software"')
    all_software = cur.fetchall()
    
    total = len(all_software)
    if total == 0:
        print("[*] No software found to clean.")
        return

    # Process in chunks
    for i in range(0, total, BATCH_SIZE):
        batch = all_software[i:i + BATCH_SIZE]
        messy_names = [item[1] for item in batch]
        
        print(f"[*] Cleaning batch {i}/{total}...")
        
        prompt = f"""
        I have a list of raw software package names from Windows. 
        I need you to convert them into the standard "Product Name" used in the NVD (National Vulnerability Database).
        Rules:
        1. Remove "Microsoft.", "Corporation", "Inc", ".app" extensions.
        2. Convert "Microsoft.WindowsCalculator" -> "Windows Calculator".
        3. Convert "SpotifyAB.SpotifyMusic" -> "Spotify".
        4. If it is a generic driver or obscure ID, return "Windows Component".
        
        Input List: {json.dumps(messy_names)}
        
        Return ONLY a JSON Object mapping Input -> Clean Name. Format: {{"Messy": "Clean"}}
        """

        try:
            response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            cleaning_map = json.loads(response.text)
            
            for sw_id, old_name in batch:
                if old_name in cleaning_map:
                    new_name = cleaning_map[old_name]
                    # Only update if the name actually changed
                    if new_name != old_name:
<<<<<<< HEAD
                        cur.execute('''
                            UPDATE "Software"
                            SET Name = %s
                            WHERE ID = %s
                            AND NOT EXISTS (
                                SELECT 1 FROM "Software" s2
                                WHERE s2.Name = %s AND s2.UserID = "Software".UserID
                            )
                            RETURNING ID;
                        ''', (new_name, sw_id, new_name))

=======
                        # Update using direct SQL
                        cur.execute('UPDATE "Software" SET Name = %s WHERE ID = %s', (new_name, sw_id))
>>>>>>> 790b354eccc883528ae291808e703a7047a74624
                        print(f"    [FIX] {old_name} -> {new_name}")
            
            conn.commit() # Commit after every batch
            time.sleep(1) # Be nice to the API

        except Exception as e:
            print(f"[!] Batch Error: {e}")
            conn.rollback()

    print("[*] Cleaning Complete.")

def serialize_user(user):
    if not user: return None
    return { "ID": user.ID, "Name": user.Name, "HashedPassword": user.HashedPassword }

def serialize_software(s):
    return {
        "ID": s.ID, "Name": s.Name, "CVSS": s.CVSS,
        "Summary": s.Summary, "Recommendation": s.Recommendation,
        "LastScan": s.LastScan, "UserID": s.UserID, "Version": s.Version
    }

# Initialize connection on import
<<<<<<< HEAD

# --- HOW TO RUN CLEANING ---
# To clean your data, uncomment the line below and run this file ONCE:
InitDataBase()
//CleanSoftwareNames()
=======
InitDataBase()

# --- HOW TO RUN CLEANING ---
# To clean your data, uncomment the line below and run this file ONCE:
# if __name__ == "__main__":
#     CleanSoftwareNames()
>>>>>>> 790b354eccc883528ae291808e703a7047a74624
