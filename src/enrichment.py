import time
import json  # <--- Added to support list storage
import nvdlib
from datetime import datetime
from database import GetAllSoftware, UpdateSoftwareByID

# --- CONFIGURATION ---
NIST_API_KEY = '3e3e6770-7a4f-44d3-b1a4-5bc6c5fb8cab'
DELAY_SECONDS = 0.6 

def EnrichData():
    print("[*] Fetching software list from database...")
    
    all_software = GetAllSoftware()
    
    # Filter: Only scan items where CVSS is None
    unscanned_software = [sw for sw in all_software if sw.CVSS is None]
    
    total_items = len(unscanned_software)
    if total_items == 0:
        print("[*] System is up to date!")
        return

    print(f"[*] Found {total_items} items to enrich.")

    for i, sw in enumerate(unscanned_software):
        sw_id = sw.ID
        sw_name = sw.Name 
        sw_version = sw.Version

        search_query = f"{sw_name} {sw_version}"
        print(f"[{i+1}/{total_items}] Searching NVD for: {search_query}...")

        try:
            results = nvdlib.searchCVE(
                keywordSearch=search_query,
                key=NIST_API_KEY,
                limit=10 
            )
            
            current_time = datetime.now()

            if results:
                print(f"    -> Found {len(results)} vulnerabilities.")
                
                max_cvss = 0.0
                cve_list_objects = [] # <--- This will hold our list of data objects
                
                for cve in results:
                    # 1. Get Score
                    score = 0.0
                    if hasattr(cve, 'v31score'): score = cve.v31score
                    elif hasattr(cve, 'v30score'): score = cve.v30score
                    elif hasattr(cve, 'v2score'): score = cve.v2score
                    
                    if score > max_cvss: max_cvss = score
                    
                    # 2. Get Description
                    desc = cve.descriptions[0].value if cve.descriptions else "No description"
                    
                    # 3. Create a Dictionary Object for this CVE
                    cve_obj = {
                        "cve_id": cve.id,
                        "cvss_score": score,
                        "description": desc,
                        "url": f"https://nvd.nist.gov/vuln/detail/{cve.id}"
                    }
                    
                    # Add to our list
                    cve_list_objects.append(cve_obj)

                # 4. Convert the LIST to a JSON STRING for storage
                # This stores the actual structure in your text field
                summary_json_string = json.dumps(cve_list_objects)

                rec_link = f"https://nvd.nist.gov/vuln/search?query={sw_name} {sw_version}"

                UpdateSoftwareByID(
                    SoftwareID=sw_id, 
                    CVSS=max_cvss, 
                    Summary=summary_json_string, # <--- Saving the JSON list here
                    Recommendation=rec_link, 
                    LastScan=current_time
                )
                print(f"    -> Saved JSON List. Max Risk: {max_cvss}")
            
            else:
                # Save an empty list "[]" if clean
                UpdateSoftwareByID(
                    SoftwareID=sw_id, 
                    CVSS=0.0, 
                    Summary="[]", 
                    Recommendation="Keep software updated.", 
                    LastScan=current_time
                )
                print("    -> Clean.")

        except Exception as e:
            print(f"[!] API Error for {sw_name}: {e}")

        time.sleep(DELAY_SECONDS)

if __name__ == "__main__":
    EnrichData()
