import winreg
import datetime
import subprocess

def get_registry_value(key, subkey, value_name):
    try:
        with winreg.OpenKey(key, subkey) as registry_key:
            value, _ = winreg.QueryValueEx(registry_key, value_name)
            return value
    except Exception:
        return "Not Found"

def get_real_os_name():
    try:
        command = "(Get-CimInstance Win32_OperatingSystem).Caption"
        result = subprocess.check_output(["powershell", "-Command", command], text=True).strip()
        return result.replace("Microsoft ", "")
    except:
        return "Unknown"

def get_experience_pack():
    try:
        command = "Get-AppxPackage -Name 'MicrosoftWindows.Client.CBS' | Select-Object -ExpandProperty Version"
        result = subprocess.check_output(["powershell", "-Command", command], text=True).strip()
        if result:
            return f"Windows Feature Experience Pack {result}"
    except:
        pass
    return "Not Found"

# --- NEW FUNCTION FOR THE AGENT UI ---
def get_os_data():
    """
    Returns OS information as a dictionary for the payload.
    """
    key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
    
    data = {}
    
    # 1. Edition
    data['edition'] = get_real_os_name()
    
    # 2. Version
    data['version'] = get_registry_value(winreg.HKEY_LOCAL_MACHINE, key_path, "DisplayVersion")
    
    # 3. Install Date
    install_timestamp = get_registry_value(winreg.HKEY_LOCAL_MACHINE, key_path, "InstallDate")
    try:
        if isinstance(install_timestamp, int):
            data['install_date'] = datetime.datetime.fromtimestamp(install_timestamp).strftime('%m/%d/%Y')
        else:
            data['install_date'] = "Unknown"
    except:
        data['install_date'] = "Unknown"

    # 4. Build
    current_build = get_registry_value(winreg.HKEY_LOCAL_MACHINE, key_path, "CurrentBuild")
    ubr = get_registry_value(winreg.HKEY_LOCAL_MACHINE, key_path, "UBR")
    data['build'] = f"{current_build}.{ubr}"

    # 5. Experience
    data['experience'] = get_experience_pack()
    
    return data

if __name__ == "__main__":
    # Test run
    print(get_os_data())
    input("\nPress Enter to exit...")
