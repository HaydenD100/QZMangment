import tkinter as tk
from tkinter import messagebox
import winreg
import subprocess
import datetime
import json
import threading
import time

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
# 2. SCANNING LOGIC
# ==========================================
def get_real_os_name():
    try:
        command = "(Get-CimInstance Win32_OperatingSystem).Caption"
        result = subprocess.check_output(["powershell", "-Command", command], text=True).strip()
        return result.replace("Microsoft ", "")
    except:
        return "Unknown"

def get_os_info():
    key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
    data = {}
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            data['edition'] = get_real_os_name()
            data['version'] = winreg.QueryValueEx(key, "DisplayVersion")[0]
            current_build = winreg.QueryValueEx(key, "CurrentBuild")[0]
            ubr = winreg.QueryValueEx(key, "UBR")[0]
            data['build'] = f"{current_build}.{ubr}"
    except Exception as e:
        data['error'] = str(e)
    return data

def get_installed_software():
    software_list = []
    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    for reg_path in registry_paths:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        sub_key_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, sub_key_name) as sub_key:
                            name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                            try:
                                version = winreg.QueryValueEx(sub_key, "DisplayVersion")[0]
                            except FileNotFoundError:
                                version = "Unknown"
                            software_list.append({"name": name, "version": version})
                    except (OSError, FileNotFoundError):
                        continue
        except Exception:
            pass
    return [dict(t) for t in {tuple(d.items()) for d in software_list}]

def send_payload(payload):
    # Simulating network request
    print(json.dumps(payload, indent=2))
    time.sleep(1.5) 
    return True

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

    btn_scan.config(state=tk.DISABLED, text="SCANNING SYSTEM...", bg=COLORS['stone'])
    status_label.config(text="Status: Scanning software registry...", bg=COLORS['sage_green'], fg=COLORS['white'])
    
    def scan_thread():
        os_data = get_os_info()
        sw_data = get_installed_software()
        
        payload = {
            "auth": {"username": username, "password": password},
            "os_info": os_data,
            "software": sw_data
        }
        
        success = send_payload(payload)
        root.after(0, lambda: finish_scan(success))

    threading.Thread(target=scan_thread, daemon=True).start()

def finish_scan(success):
    btn_scan.config(state=tk.NORMAL, text="SCAN NOW", bg=COLORS['sage_green'])
    
    if success:
        status_label.config(text="Status: Upload Complete ✔", bg=COLORS['mint_accent'], fg=COLORS['deep_emerald'])
        messagebox.showinfo("Success", "System audit completed successfully.")
    else:
        status_label.config(text="Status: Connection Failed ✖", bg=COLORS['critical'], fg=COLORS['white'])

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
# --- CHANGED: ipady increased to 10 ---
status_label.pack(side="bottom", fill="x", ipady=10)

root.mainloop()