import subprocess
import json
import logging
import os
import winreg
import xml.etree.ElementTree as ET

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def get_store_apps_current_user():
    """
    Scans only the current logged-in user's apps (PowerShell).
    """
    ps_command = r"""
    # Force array @() to prevent null errors
    $apps = @(Get-AppxPackage)
    
    $output = @()
    
    foreach ($app in $apps) {
        $output += [PSCustomObject]@{
            Name = $app.Name
            PackageFullName = $app.PackageFullName
            Version = $app.Version
            InstallLocation = $app.InstallLocation
            IsStore = $true
        }
    }
    
    $output | ConvertTo-Json -Depth 2
    """
    
    try:
        # print("--- Scanning Store Apps (PowerShell) ---") # Commented out for cleaner output
        result = subprocess.run(
            ["powershell", "-Command", ps_command], 
            capture_output=True, text=True, check=True, encoding='utf-8'
        )
        
        if not result.stdout.strip():
            return []
            
        return json.loads(result.stdout)
    except Exception as e:
        return []

def get_registry_apps_native():
    """
    Classic Win32 Apps (Registry Scan).
    """
    apps = {}
    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall")
    ]

    # print("--- Scanning Registry (Classic Apps) ---") # Commented out for cleaner output

    for root, path in registry_paths:
        try:
            with winreg.OpenKey(root, path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            try:
                                name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                try:
                                    version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                                except FileNotFoundError:
                                    version = "Unknown"
                                
                                name = name.strip()
                                if name:
                                    apps[name] = {"Name": name, "Version": version}
                            except FileNotFoundError:
                                continue 
                    except Exception:
                        continue
        except Exception:
            pass
    return apps

def get_exe_from_manifest(folder_path):
    """
    Reads AppxManifest.xml to find the actual executable defined by the developer.
    """
    manifest_path = os.path.join(folder_path, "AppxManifest.xml")
    
    if not os.path.exists(manifest_path):
        return None

    try:
        tree = ET.parse(manifest_path)
        root = tree.getroot()
        
        # Strip namespaces
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1] 

        applications = root.find('Applications')
        if applications is not None:
            for app in applications.findall('Application'):
                executable = app.get('Executable')
                if executable:
                    return executable
    except Exception:
        pass
        
    return None

def get_real_version_from_folder(folder_path):
    """
    Finds the executable via Manifest or Size, then reads the version header.
    """
    if not folder_path or not os.path.exists(folder_path):
        return None

    # 1. Try Manifest
    exe_name = get_exe_from_manifest(folder_path)
    
    # 2. Fallback: Largest EXE
    if not exe_name:
        exe_files = []
        for root, dirs, files in os.walk(folder_path):
            for f in files:
                if f.lower().endswith(".exe"):
                    full_p = os.path.join(root, f)
                    exe_files.append((full_p, os.path.getsize(full_p)))
        
        if exe_files:
            exe_files.sort(key=lambda x: x[1], reverse=True)
            exe_name = os.path.basename(exe_files[0][0])

    if not exe_name:
        return None

    full_path = os.path.join(folder_path, exe_name)
    
    # Handle relative paths
    if not os.path.exists(full_path):
         full_path = os.path.join(folder_path, exe_name)

    if os.path.exists(full_path):
        cmd = f"(Get-Item '{full_path}' -ErrorAction SilentlyContinue).VersionInfo.ProductVersion"
        try:
            res = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
            return res.stdout.strip()
        except:
            return None
            
    return None

# --- MAIN ---
if __name__ == "__main__":
    final_list = {}

    # 1. Registry Scan
    reg_apps = get_registry_apps_native()
    final_list.update(reg_apps)

    # 2. Store Scan
    store_apps_raw = get_store_apps_current_user()
    
    if store_apps_raw is None: store_apps_raw = []
    if isinstance(store_apps_raw, dict): store_apps_raw = [store_apps_raw]

    # 3. Process Store Apps with XML Logic
    for app in store_apps_raw:
        raw_name = app.get('Name', '')
        install_location = app.get('InstallLocation')
        version = app.get('Version')
        
        display_name = raw_name

        # If version is missing/generic, use the XML+File reader
        if (not version or version == "0.0.0.0") and install_location:
             real_ver = get_real_version_from_folder(install_location)
             if real_ver:
                 version = real_ver

        final_list[display_name] = {
            "Name": display_name,
            "Version": version
        }

    # 4. Output
    print(f"\n{'Name':<60} | {'Version':<15}")
    print("-" * 80)
    
    sorted_keys = sorted(final_list.keys(), key=lambda s: s.lower())
    
    count = 0
    for key in sorted_keys:
        item = final_list[key]
        print(f"{item['Name']:<60} | {str(item['Version']):<15}")
        count += 1
            
    print("-" * 80)
    print(f"Total Items Found: {count}")