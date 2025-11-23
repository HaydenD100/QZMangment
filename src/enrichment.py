import time
import re
import nvdlib
from datetime import datetime
from database import GetAllSoftware, UpdateSoftwareByID

# --- CONFIGURATION ---
NIST_API_KEY = '3e3e6770-7a4f-44d3-b1a4-5bc6c5fb8cab'
DELAY_SECONDS = 0.6 

def CleanName(raw_name):
    """
    Transforms 'SpotifyAB.SpotifyMusic' -> 'Spotify Music'
    Transforms 'Microsoft.WindowsCalculator_8weky...' -> 'Windows Calculator'
    """
    # 1. Remove version numbers or hashes (often after an underscore or at end)
    name = raw_name.split('_')[0] # Remove _8weky...
    
    # 2. Split by dot (common in Package Names)
    if '.' in name:
        parts = name.split('.')
        # Usually the last part is the product name (e.g. SpotifyMusic)
        name = parts[-1]

    # 3. Split CamelCase (SpotifyMusic -> Spotify Music)
    name = re.sub(r'(?<!^)(?=[A-Z])', ' ', name)

    return name.strip()

def EnrichData():
    print("[*] Fetching software list...")
    all_software = GetAllSoftware()
    
    # Filter: Only scan items where CVSS is None
    unscanned_software = [sw for sw in all_software if sw.CVSS is None]
    total = len(unscanned_software)
    
    if total == 0:
        print("[*] No new software to scan.")
        return

    print(f"[*] Found {total} items. Starting analysis...")

    for i, sw in enumerate(unscanned_software):
        sw_id = sw.ID
        original_name = sw.Name
        version = sw.Version
        
        # --- STRATEGY: TRY ORIGINAL NAME, THEN TRY CLEAN NAME ---
        search_candidates = [original_name]
        
        clean_name = CleanName(original_name)
        if clean_name != original_name:
            search_candidates.append(clean_name)

        results = []
        used_name = ""

        for search_name in search_candidates:
            query = f"{search_name} {version}"
            print(f"[{i+1}/{total}] Attempting search: '{query}'...")
            
            try:
                # Remove limit=1 to get ALL CVEs
                results = nvdlib.searchCVE(
                    keywordSearch=query,
                    key=NIST_API_KEY,
                    limit=10 # Get top 10 relevant CVEs
                )
                if results:
                    used_name = search_name
                    break # Found something! Stop trying other names.
                
                time.sleep(DELAY_SECONDS) # Sleep between attempts
                
            except Exception as e:
                print(f"[!] API Error: {e}")
                time.sleep(DELAY_SECONDS)

        # --- PROCESS RESULTS ---
        current_time = datetime.now()

        if results:
            print(f"    -> Found {len(results)} CVEs using name '{used_name}'")
            
            max_cvss = 0.0
            summary_report = []
            
            # Loop through found CVEs to build a report
            for cve in results:
                # Get Score
                score = 0.0
                if hasattr(cve, 'v31score'): score = cve.v31score
                elif hasattr(cve, 'v30score'): score = cve.v30score
                elif hasattr(cve, 'v2score'): score = cve.v2score
                
                # Update Max Score
                if score > max_cvss: max_cvss = score
                
                # Add to text report
                desc = cve.descriptions[0].value if cve.descriptions else "No desc"
                # Limit desc length to keep DB clean
                short_desc = (desc[:100] + '..') if len(desc) > 100 else desc
                summary_report.append(f"[{cve.id} | Score: {score}] {short_desc}")

            # Create the final blob for the Summary field
            final_summary = "\n".join(summary_report[:5]) # Top 5 only
            if len(results) > 5: final_summary += f"\n...and {len(results)-5} more."
            
            rec_link = f"https://nvd.nist.gov/vuln/search?query={used_name} {version}"

            UpdateSoftwareByID(sw_id, max_cvss, final_summary, rec_link, current_time)

        else:
            print(f"    -> Clean. No vulnerabilities found.")
            UpdateSoftwareByID(sw_id, 0.0, "No CVEs found for this version.", "N/A", current_time)

        time.sleep(DELAY_SECONDS)

if __name__ == "__main__":
    EnrichData()
