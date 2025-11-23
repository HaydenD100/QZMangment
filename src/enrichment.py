import time
import nvdlib
from datetime import datetime

# Import functions directly from your database.py
# We don't need SQL queries here anymore!
from database import GetAllSoftware, UpdateSoftwareByID

# --- CONFIGURATION ---
NIST_API_KEY = '3e3e6770-7a4f-44d3-b1a4-5bc6c5fb8cab'
DELAY_SECONDS = 0.6 

def EnrichData():
    print("[*] fetching software list from database...")
    
    # 1. Get ALL software objects
    all_software = GetAllSoftware()
    
    # 2. Filter in Python: Only keep items where CVSS is None
    # We use the object attribute .CVSS (defined in your GetAllSoftware function)
    unscanned_software = [sw for sw in all_software if sw.CVSS is None]
    
    total_items = len(unscanned_software)
    
    if total_items == 0:
        print("[*] System is up to date! No new software to scan.")
        return

    print(f"[*] Found {total_items} new items to enrich.")
    print(f"[*] Estimated time: {(total_items * DELAY_SECONDS) / 60:.1f} minutes.")

    # 3. Iterate through the objects
    for i, sw in enumerate(unscanned_software):
        # Access attributes directly from the class object
        sw_id = sw.ID
        sw_name = sw.Name
        sw_version = sw.Version

        search_query = f"{sw_name} {sw_version}"
        print(f"[{i+1}/{total_items}] Searching NVD for: {search_query}...")

        try:
            results = nvdlib.searchCVE(
                keywordSearch=search_query,
                key=NIST_API_KEY,
                limit=1,
                sortKeywordSearch=True 
            )
            
            current_time = datetime.now()

            if results:
                cve = results[0]
                
                # Priority: V3.1 -> V3.0 -> V2.0
                score = 0.0
                if hasattr(cve, 'v31score'): score = cve.v31score
                elif hasattr(cve, 'v30score'): score = cve.v30score
                elif hasattr(cve, 'v2score'): score = cve.v2score
                
                desc = cve.descriptions[0].value if cve.descriptions else "No description"
                rec_link = f"https://nvd.nist.gov/vuln/detail/{cve.id}"

                # Update using your existing function
                UpdateSoftwareByID(
                    SoftwareID=sw_id, 
                    CVSS=score, 
                    Summary=desc, 
                    Recommendation=rec_link, 
                    LastScan=current_time
                )
                print(f"    -> Found CVE! Score: {score}")
            
            else:
                # Mark as 0.0 to prevent re-scanning next time
                UpdateSoftwareByID(
                    SoftwareID=sw_id, 
                    CVSS=0.0, 
                    Summary="No known vulnerabilities found in NVD.", 
                    Recommendation="Keep software updated.", 
                    LastScan=current_time
                )
                print("    -> Clean. No CVEs found.")

        except Exception as e:
            print(f"[!] API Error for {sw_name}: {e}")

        time.sleep(DELAY_SECONDS)

if __name__ == "__main__":
    EnrichData()
