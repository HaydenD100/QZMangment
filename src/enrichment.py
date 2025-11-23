import time
import nvdlib
from datetime import datetime
from database import GetAllSoftware, UpdateSoftwareByID

# --- CONFIGURATION ---
NIST_API_KEY = '3e3e6770-7a4f-44d3-b1a4-5bc6c5fb8cab'
DELAY_SECONDS = 0.6 

def EnrichData():
    print("[*] Fetching software list from database...")
    
    # 1. Get ALL software objects
    all_software = GetAllSoftware()
    
    # 2. Filter: Only scan items where CVSS is None (New items)
    unscanned_software = [sw for sw in all_software if sw.CVSS is None]
    
    total_items = len(unscanned_software)
    
    if total_items == 0:
        print("[*] System is up to date! No new software to scan.")
        return

    print(f"[*] Found {total_items} items to enrich using Clean Names.")
    print(f"[*] Estimated time: {(total_items * DELAY_SECONDS) / 60:.1f} minutes.")

    # 3. Iterate through the objects
    for i, sw in enumerate(unscanned_software):
        sw_id = sw.ID
        # These are now the CLEAN names from your DB (e.g. "Spotify")
        sw_name = sw.Name 
        sw_version = sw.Version

        search_query = f"{sw_name} {sw_version}"
        print(f"[{i+1}/{total_items}] Searching NVD for: {search_query}...")

        try:
            # Fetch the top 10 most relevant CVEs
            results = nvdlib.searchCVE(
                keywordSearch=search_query,
                key=NIST_API_KEY,
                limit=10 
            )
            
            current_time = datetime.now()

            if results:
                print(f"    -> Found {len(results)} potential vulnerabilities.")
                
                max_cvss = 0.0
                report_lines = []
                
                # Loop through results to Aggregate Data
                for cve in results:
                    # 1. Get Score (V3.1 > V3.0 > V2.0)
                    score = 0.0
                    if hasattr(cve, 'v31score'): score = cve.v31score
                    elif hasattr(cve, 'v30score'): score = cve.v30score
                    elif hasattr(cve, 'v2score'): score = cve.v2score
                    
                    # 2. Track the Highest Risk
                    if score > max_cvss:
                        max_cvss = score
                    
                    # 3. Format the Description for the report
                    cve_id = cve.id
                    desc = cve.descriptions[0].value if cve.descriptions else "No description"
                    # Truncate long descriptions to keep the report readable
                    short_desc = (desc[:120] + '...') if len(desc) > 120 else desc
                    
                    report_lines.append(f"[{cve_id} | Score: {score}] {short_desc}")

                # 4. Create the Summary Report (Top 5 only)
                final_summary = "\n\n".join(report_lines[:5])
                
                # Add a footer if there are more
                if len(results) > 5:
                    final_summary += f"\n\n...and {len(results) - 5} more vulnerabilities found."

                # 5. Create a dynamic link for the user to see full details
                rec_link = f"https://nvd.nist.gov/vuln/search?query={sw_name} {sw_version}"

                # 6. Update Database
                UpdateSoftwareByID(
                    SoftwareID=sw_id, 
                    CVSS=max_cvss, 
                    Summary=final_summary, 
                    Recommendation=rec_link, 
                    LastScan=current_time
                )
                print(f"    -> Saved. Max Risk: {max_cvss}")
            
            else:
                # No vulnerabilities found
                UpdateSoftwareByID(
                    SoftwareID=sw_id, 
                    CVSS=0.0, 
                    Summary="No known vulnerabilities found in NVD for this specific version.", 
                    Recommendation="Keep software updated.", 
                    LastScan=current_time
                )
                print("    -> Clean. No CVEs found.")

        except Exception as e:
            print(f"[!] API Error for {sw_name}: {e}")

        # Respect Rate Limits
        time.sleep(DELAY_SECONDS)

if __name__ == "__main__":
    EnrichData()
