from ETS2LA.Utils.Console.colors import *
from ETS2LA.Utils.shell import ExecuteCommand
import ETS2LA.Networking.cloud as cloud
from importlib.metadata import version
import traceback
import os

malicious_packages = {
    "ultralytics": ["8.3.41", "8.3.42", "8.3.45", "8.3.46"]
}

def CheckForMaliciousPackages():
    for package in malicious_packages.keys():
        try:
            ver = version(package)
            if ver in malicious_packages[package]:
                print(RED + f"Your installed version of the '{package}' package might be malicious! Trying to remove it... (Package Version: {ver})" + END)
                ExecuteCommand(f"pip uninstall {package} -y & pip cache purge & pip install {package} --force-reinstall")
                cloud.SendCrashReport(package, f"Successfully updated a malicious package.", f"From version {ver} to the latest version.")
                print(GREEN + f"Successfully updated the '{package}' package to the latest version." + END)
        except:
            cloud.SendCrashReport(package, "Update malicious package error.", traceback.format_exc())
            print(RED + f"Unable to check the version of the '{package}' package. Please update your '{package}' package manually if you have one of these versions installed: {malicious_packages[package]}" + END)

def FixModule(module, ver, url):
    try:
        cur_ver = version(module)
    except:
        cur_ver = "0.0.0"
        
    if cur_ver < ver:
        print(f"{GREEN} -- Please wait, we need to install the correct version of:{YELLOW} {module} {GREEN} -- {END}")
        ExecuteCommand(f"pip install {url}")
        