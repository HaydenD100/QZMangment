import tkinter as tk
from tkinter import messagebox
import json
import threading
import time
import sys
import requests # REQUIRED: pip install requests

# --- IMPORT EXTERNAL MODULES ---
import agent_logic  # Your software scanner
import os_check     # Your OS scanner
# -------------------------------

# ==========================================
# 1. DESIGN SYSTEM
# ==========================================
COLORS = {
    "deep_emerald": "#064e3b",
    "forest_green": "#065f46",
    "sage_green":   "#047857",
    "mint_accent":  "#10b981",
    "ivory_cream":  "#fef7ed",
    "warm_cream":   "#fffbeb",
    "charcoal":     "#1f2937",
    "slate":        "#374151",
    "stone":        "#6b7280",
    "critical":     "#dc2626",
    "white":        "#ffffff"
}

FONTS = {
    "header": ("Segoe UI", 16, "bold"),
    "label":  ("Segoe UI", 10, "bold"),
    "entry":  ("Segoe UI", 10),
    "button": ("Segoe UI", 11, "bold"),
    "status": ("Segoe UI", 9)
}

# ==========================================
# 2. NETWORK LOGIC (PRODUCTION)
# ==========================================
def send_payload(payload):
    """
    Sends the JSON payload to the Flask Database Server.
    """
    # Ensure this matches your running Flask server URL
    url = "http://127.0.0.1:5000/AgentSend"
    
    try:
        print(f" [NET] Sending data to {url}...")
        
        # Set timeout to 10 seconds to prevent hanging
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            print(" [NET] Success: Server accepted payload.")
            return True
        else:
            print(f" [NET] Server Error ({response.status_code}): {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(" [NET] Connection Refused. Is the Flask server running?")
        return False
    except Exception as e:
        print(f" [NET] Error: {e}")
        return False

# ==========================================
# 3. GUI LOGIC
# ==========================================
def on_enter(e):
    if btn_scan['state'] == 'normal':
        btn_scan['background'] = COLORS['forest_green']

def on_leave(e):
    if btn_scan['state'] == 'normal':
        btn_scan['background'] = COLORS['sage_green']

def start_scan():
    username = entry_user.get()
    password = entry_pass.get()

    if not username or not password:
        messagebox.showwarning("Validation", "Please fill in all fields.")
        return

    # UI: Loading State
    btn_scan.config(state=tk.DISABLED, text="SCANNING SYSTEM...", bg=COLORS['stone'])
    status_label.config(text="Status: Starting System Scan...", bg=COLORS['sage_green'], fg=COLORS['white'])
    
    def scan_thread():
        try:
            print("\n" + "="*40)
            print(" 1. GATHERING OS INFO")
            print("="*40)
            
            # 1. Get OS Info
            os_data = os_check.get_os_data()
            print(f" [+] OS:    {os_data['edition']}")
            print(f" [+] Build: {os_data['build']}")
            
            print("\n" + "="*40)
            print(" 2. STARTING SOFTWARE SCAN")
            print("="*40)
            status_label.config(text="Status: Scanning installed software...")
            
            # 2. Get Software
            sw_data = agent_logic.scan_all_software()
            print(f"\n [OK] Scan Complete. Found {len(sw_data)} items.")
            
            status_label.config(text="Status: Uploading to Database...")
            
            # 3. Build Payload
            payload = {
                "auth": {
                    "username": username, 
                    "password": password
                },
                "os_info": os_data,        # Includes Edition, Version, Build, InstallDate
                "installed_software": sw_data
            }
            
            # 4. Send Network Request
            success = send_payload(payload)
            root.after(0, lambda: finish_scan(success))
            
        except Exception as e:
            print(f"Critical Error: {e}")
            root.after(0, lambda: finish_scan(False))

    threading.Thread(target=scan_thread, daemon=True).start()

def finish_scan(success):
    btn_scan.config(state=tk.NORMAL, text="SCAN NOW", bg=COLORS['sage_green'])
    
    if success:
        status_label.config(text="Status: Upload Complete ✔", bg=COLORS['mint_accent'], fg=COLORS['deep_emerald'])
        messagebox.showinfo("Success", "Scan complete and data uploaded to database successfully.")
    else:
        status_label.config(text="Status: Upload Failed (Check Console) ✖", bg=COLORS['critical'], fg=COLORS['white'])
        messagebox.showerror("Connection Error", "Could not send data to server.\nCheck if the server is running and credentials are correct.")

# ==========================================
# 4. UI CONSTRUCTION
# ==========================================
root = tk.Tk()
root.title("Security Agent")
root.geometry("400x350")
root.configure(bg=COLORS['ivory_cream'])
root.resizable(False, False) 

# -- Header --
header_frame = tk.Frame(root, bg=COLORS['ivory_cream'])
header_frame.pack(pady=(25, 20))

tk.Label(header_frame, text="System Audit Agent", 
         font=FONTS['header'], 
         bg=COLORS['ivory_cream'], 
         fg=COLORS['deep_emerald']).pack()

tk.Label(header_frame, text="Secure Local Scanner", 
         font=("Segoe UI", 9), 
         bg=COLORS['ivory_cream'], 
         fg=COLORS['stone']).pack()

# -- Form Container --
form_frame = tk.Frame(root, bg=COLORS['ivory_cream'])
form_frame.pack(pady=10, padx=40, fill="x")

# Username
tk.Label(form_frame, text="USERNAME", font=FONTS['label'], 
         bg=COLORS['ivory_cream'], fg=COLORS['slate']).pack(anchor="w")
entry_user = tk.Entry(form_frame, font=FONTS['entry'], 
                      bg=COLORS['warm_cream'], fg=COLORS['charcoal'], 
                      relief="flat", bd=1, highlightthickness=1, highlightbackground=COLORS['stone'])
entry_user.pack(fill="x", pady=(2, 10), ipady=4)

# Password
tk.Label(form_frame, text="PASSWORD", font=FONTS['label'], 
         bg=COLORS['ivory_cream'], fg=COLORS['slate']).pack(anchor="w")
entry_pass = tk.Entry(form_frame, show="•", font=FONTS['entry'], 
                      bg=COLORS['warm_cream'], fg=COLORS['charcoal'],
                      relief="flat", bd=1, highlightthickness=1, highlightbackground=COLORS['stone'])
entry_pass.pack(fill="x", pady=(2, 20), ipady=4)

# -- Action Button --
btn_scan = tk.Button(root, text="SCAN NOW", 
                     font=FONTS['button'], 
                     bg=COLORS['sage_green'], 
                     fg=COLORS['white'],
                     activebackground=COLORS['forest_green'], 
                     activeforeground=COLORS['white'],
                     relief="flat", 
                     cursor="hand2",
                     command=start_scan)
btn_scan.pack(fill="x", padx=40, ipady=5, pady=(0, 30))

btn_scan.bind("<Enter>", on_enter)
btn_scan.bind("<Leave>", on_leave)

# -- Status Bar --
status_label = tk.Label(root, text="Ready to scan", 
                        font=FONTS['status'], 
                        bg=COLORS['charcoal'], 
                        fg=COLORS['white'], 
                        anchor="center")
status_label.pack(side="bottom", fill="x", ipady=10)

if __name__ == "__main__":
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nAgent stopped by user.")
        sys.exit(0)
