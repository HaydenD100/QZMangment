import winreg
import datetime
import subprocess

def get_registry_value(key, subkey, value_name):
    try:
        registry_key = winreg.OpenKey(key, subkey)
        value, _ = winreg.QueryValueEx(registry_key, value_name)
        winreg.CloseKey(registry_key)
        return value
    except Exception as e:
        return "Not Found"

def get_real_os_name():
    # The Registry 'ProductName' often lies and says 'Windows 10' for compatibility.
    # We use PowerShell to ask WMI (Windows Management Instrumentation) for the true caption.
    try:
        command = "(Get-CimInstance Win32_OperatingSystem).Caption"
        # This typically returns "Microsoft Windows 11 Home"
        result = subprocess.check_output(["powershell", "-Command", command], text=True).strip()
        # Optional: Remove "Microsoft " from the start to match your format exactly
        return result.replace("Microsoft ", "")
    except:
        # Fallback if PowerShell fails, though unlikely on Windows 11
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

def get_windows_info():
    key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
    
    # 1. Edition (Fixed method)
    edition = get_real_os_name()
    
    # 2. Version (DisplayVersion)
    version = get_registry_value(winreg.HKEY_LOCAL_MACHINE, key_path, "DisplayVersion")
    
    # 3. Installed On
    install_timestamp = get_registry_value(winreg.HKEY_LOCAL_MACHINE, key_path, "InstallDate")
    try:
        install_date = datetime.datetime.fromtimestamp(install_timestamp).strftime('%m/%d/%Y')
    except:
        install_date = "Unknown"

    # 4. OS Build
    current_build = get_registry_value(winreg.HKEY_LOCAL_MACHINE, key_path, "CurrentBuild")
    ubr = get_registry_value(winreg.HKEY_LOCAL_MACHINE, key_path, "UBR")
    full_build = f"{current_build}.{ubr}"

    # 5. Experience
    experience = get_experience_pack()

    # --- Output ---
    print(f"{'Edition':<15} {edition}")
    print(f"{'Version':<15} {version}")
    print(f"{'Installed on':<15} {install_date}")
    print(f"{'OS build':<15} {full_build}")
    print(f"{'Experience':<15} {experience}")

if __name__ == "__main__":
    print("Fetching Corrected System Information...\n")
    get_windows_info()
    input("\nPress Enter to exit...")