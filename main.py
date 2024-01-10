'''
The main file that runs the programs loop.
'''

# This section is for modules that I've added later as they might 
# not have been installed yet

import src.settings as settings
import src.variables as variables # Stores all main variables for the program
if settings.GetSettings("User Interface", "hide_console", False) == True:
    import win32gui, win32con
    window_found = False
    target_text = "/venv/Scripts/python"
    top_windows = []
    win32gui.EnumWindows(lambda hwnd, top_windows: top_windows.append((hwnd, win32gui.GetWindowText(hwnd))), top_windows)
    for hwnd, window_text in top_windows:
        if target_text in window_text:
            window_found = True
            variables.CONSOLENAME = hwnd
            break
    if window_found == False:
        print("Console window not found, unable to hide!")
    else:
        print(f"Console Name: {window_text}, Console ID: {hwnd}")
        win32gui.ShowWindow(variables.CONSOLENAME, win32con.SW_HIDE)

import os
try:
    import colorama
except:
    os.system("pip install colorama")
    import colorama

try:
    import matplotlib
except:
    os.system("pip install matplotlib")
    import matplotlib

try:
    import webview
except:
    os.system("pip install pywebview")
    import webview

try:
    import vdf
except:
    os.system("pip install vdf")
    import vdf

try:
    import deep_translator
except:
    os.system("pip install deep_translator")
    import deep_translator

try: 
    import babel
except:
    os.system("pip install babel")
    import babel

# Check that all requirments from requirments.txt are installed
import pkg_resources
with open(variables.PATH + r"\requirements.txt") as f:
    requirements = f.read().splitlines()

installed = [pkg.key for pkg in pkg_resources.working_set]
requirementsset = set(requirements)
installedset = set(installed)
missing = requirementsset - installedset

if missing:
    for modules in missing:
        if "deep_translator" in modules:
            pass
        elif "--upgrade --no-cache-dir gdown" in modules:
            pass
        elif "sv_ttk" in modules:
            pass
        elif "playsound2" in modules:
            os.system("pip uninstall -y playsound")
            os.system("pip install playsound2")
        else:
            print("installing" + " " + modules)
            os.system("pip install" + " " + modules)
else:
    pass

import requests
def UpdateChecker():
    currentVer = variables.VERSION.split(".")
    url = "https://raw.githubusercontent.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/main/version.txt"
    try:
        remoteVer = requests.get(url).text.strip().split(".")
    except:
        print("Failed to check for updates")
        print("Please check your internet connection and try again later")
        return
    if currentVer[0] < remoteVer[0]:
        update = True
    elif currentVer[1] < remoteVer[1]:
        update = True
    elif currentVer[2] < remoteVer[2]:
        update = True
    else:
        update = False
    
    print(f"Current version: {'.'.join(currentVer)}")
    print(f"Remote version: {'.'.join(remoteVer)}")
    print(f"Update available: {update}")
    if update:
        print(f"Changelog:\n{requests.get('https://raw.githubusercontent.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/main/changelog.txt').text}")
        changelog = requests.get("https://raw.githubusercontent.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist/main/changelog.txt").text
        from tkinter import messagebox
        if messagebox.askokcancel("Updater", (f"We have detected an update, do you want to install it?\nCurrent - {'.'.join(currentVer)}\nUpdated - {'.'.join(remoteVer)}\n\nChangelog:\n{changelog}")):
            os.system("git stash")
            os.system("git pull")
            if messagebox.askyesno("Updater", ("The update has been installed and the application needs to be restarted. Do you want to quit the app?")):
                quit()
        else:
            pass

try:
    devmode = settings.GetSettings("Dev", "disable_update_checker", False)
    if devmode == False:
        UpdateChecker()
except Exception as ex:
    # If the exception is for the quit command, then do that
    if ex.args == ("quit",):
        quit()

# Check tkinter tcl version
import tkinter as tk
from tkinter import messagebox
tcl = tk.Tcl()
acceptedVersions = ["8.6.11", "8.6.12", "8.6.13"]
version = str(tcl.call('info', 'patchlevel'))
if version not in acceptedVersions:
    messagebox.showwarning("Warning", f"Your tkinter version ({version} is not >= 8.6.11) is too old. Windows scaling will be broken with this version.")
    print(f"Your tkinter version ({version} is not >= 8.6.11) is too old. Windows scaling will be broken with this version.")

# Load the UI framework
import src.mainUI as mainUI
mainUI.CreateRoot()

import src.loading as loading # And then create a loading window

# Load the rest of the modules
import sys
import time
import json
from src.logger import print
import src.logger as logger
import traceback
import src.translator as translator
import src.controls as controls
import psutil
import cv2

logger.printDebug = settings.GetSettings("logger", "debug")
if logger.printDebug == None:
    logger.printDebug = False
    settings.CreateSettings("logger", "debug", False)
    

def GetEnabledPlugins():
    global enabledPlugins
    enabledPlugins = settings.GetSettings("Plugins", "Enabled")
    if enabledPlugins == None:
        enabledPlugins = [""]

def FindPlugins(reloadFully=False):
    global plugins
    global pluginObjects
    
    # Find plugins
    path = os.path.join(variables.PATH, "plugins")
    plugins = []
    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            # Check for main.py
            if "main.py" in os.listdir(os.path.join(path, file)):
                # Check for PluginInformation class
                try:
                    pluginPath = "plugins." + file + ".main"
                    plugin = __import__(pluginPath, fromlist=["PluginInformation"])
                    if plugin.PluginInfo.type == "dynamic":
                        if plugin.PluginInfo.name in enabledPlugins:
                            plugins.append(plugin.PluginInfo)
                except Exception as ex:
                    print(str(ex.args) + f" [{file}]")
                    pass

    pluginObjects = []
    for plugin in plugins:
        pluginObjects.append(__import__("plugins." + plugin.name + ".main", fromlist=["plugin", "UI", "PluginInfo", "onEnable"]))
        pluginObjects[-1].onEnable()
        
def ReloadPluginCode():
    # Use the inbuilt python modules to reload the code of the plugins
    import importlib
    for plugin in pluginObjects:
        try:
            importlib.reload(plugin)
        except Exception as ex:
            print(ex.args)
            pass
    print("Reloaded plugin code.")
    print("Reloading UI root code...")
    try:
        mainUI.DeleteRoot()
        importlib.reload(mainUI)
        mainUI.CreateRoot()
        mainUI.drawButtons()
    except Exception as ex:
        print(ex.args)
        pass
    print("Reloaded UI root code.")

def RunOnEnable():
    for plugin in pluginObjects:
        try:
            plugin.onEnable()
        except Exception as ex:
            print(ex.args)
            pass
        

def UpdatePlugins(dynamicOrder, data):
    for plugin in pluginObjects:
        try:
            if plugin.PluginInfo.dynamicOrder == dynamicOrder:
                startTime = time.time()
                data = plugin.plugin(data)
                endTime = time.time()
                if data == None:
                    print(f"Plugin '{plugin.PluginInfo.name}' returned NoneType instead of a the data variable. Please make sure that you return the data variable.")
                else:
                    data["executionTimes"][plugin.PluginInfo.name] = endTime - startTime
                        
        except Exception as ex:
            print(ex.args + f"[{plugin.PluginInfo.name}]")
            pass
    return data


def InstallPlugins():
    global startInstall
    global loadingWindow
    
    list = settings.GetSettings("Plugins", "Installed")
    if list == None:
        settings.CreateSettings("Plugins", "Installed", [])
    
    # Find plugins
    path = os.path.join(variables.PATH, "plugins")
    installers = []
    pluginNames = []
    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            # Check for main.py
            if "main.py" in os.listdir(os.path.join(path, file)):
                # Check for PluginInformation class
                try:
                    # Get installers for plugins that are not installed
                    if file not in settings.GetSettings("Plugins", "Installed"):
                        pluginPath = "plugins." + file + ".install"
                        try:
                            pluginNames.append(f"{file}")
                            installers.append(__import__(pluginPath, fromlist=["install"]))
                        except: # No installer
                            pass
                        
                    
                except Exception as ex:
                    print(ex.args)
                    pass
    
    if installers == []:
        return
    
    import tkinter as tk
    from tkinter import ttk
    
    try:
        loadingWindow.destroy()
    except:
        pass
    
    # Create a new tab for the installer
    installFrame = ttk.Frame(mainUI.pluginNotebook, width=600, height=520)
    installFrame.pack(anchor=tk.CENTER, expand=True, fill=tk.BOTH)
    mainUI.pluginNotebook.add(installFrame, text="Plugin Installer")
    mainUI.pluginNotebook.select(mainUI.pluginNotebook.tabs()[-1])
    
    ttk.Label(installFrame, text="The app has detected plugins that have not yet been installed.").pack()
    ttk.Label(installFrame, text="Please install them before continuing.").pack()
    ttk.Label(installFrame, text="").pack()
    ttk.Label(installFrame, text="WARNING: Make sure you trust the authors of the plugins.").pack()
    ttk.Label(installFrame, text="If you are at all skeptical then you can see the install script at").pack()
    ttk.Label(installFrame, text="app/plugins/<plugin name>/installer.py").pack()
    ttk.Label(installFrame, text="").pack()
    
    startInstall = False
    def SetInstallToTrue():
        global startInstall
        startInstall = True
    ttk.Button(installFrame, text="Install plugins", command=lambda: SetInstallToTrue()).pack()
    
    ttk.Label(installFrame, text="").pack()
    ttk.Label(installFrame, text="The following plugins require installation: ").pack()
    # Make tk list object
    listbox = tk.Listbox(installFrame, width=75, height=30)
    listbox.pack()
    # Add the plugins there
    for plugin in pluginNames:
        listbox.insert(tk.END, plugin)
    # Center the listbox text
    listbox.config(justify=tk.CENTER)
    
    while not startInstall:
        mainUI.root.update()
    
    # Destroy all the widgets
    for child in installFrame.winfo_children():
        child.destroy()
        
    # Create the progress indicators
    ttk.Label(installFrame, text="\n\n\n\n\n\n\n").pack()
    currentPlugin = tk.StringVar(installFrame)
    currentPlugin.set("Installing plugins...")
    ttk.Label(installFrame, textvariable=currentPlugin).pack()
    bar = ttk.Progressbar(installFrame, orient=tk.HORIZONTAL, length=200, mode='determinate')
    bar.pack(pady=15)
    percentage = tk.StringVar(installFrame)
    ttk.Label(installFrame, textvariable=percentage).pack()
    ttk.Label(installFrame, text="").pack()
    ttk.Label(installFrame, text="This may take a while...").pack()
    ttk.Label(installFrame, text="For more information check the console.").pack()
    
    mainUI.root.update()
    
    loadingWindow = loading.LoadingWindow("Installing plugins...")
    
    index = 0
    import progress.bar as Bar
    with Bar.PixelBar("Installing plugins...", max=len(installers)) as progressBar:
        for installer, name in zip(installers, pluginNames):
            sys.stdout.write(f"\nInstalling '{name}'...\n")
            currentPlugin.set(f"Installing '{name}'...")
            bar.config(value=(index / len(installers)) * 100)
            percentage.set(f"{round((index / len(installers)) * 100)}%")
            mainUI.root.update()
            installer.install()
            settings.AddToList("Plugins", "Installed", name.split(" - ")[0])
            index += 1
            loadingWindow.update(text=f"Installing '{name}'...")
            os.system("cls")
            progressBar.next()
    
    # Destroy all the widgets
    for child in installFrame.winfo_children():
        child.destroy()
        
    # Remove the tab
    settings.RemoveFromList("Plugins", "OpenTabs", "Plugin Installer")
    variables.RELOADPLUGINS = True
        

def CheckForONNXRuntimeChange():
    change = settings.GetSettings("SwitchLaneDetectionDevice", "switchTo")
    if change != None:
        if change == "GPU":
            loadingWindow.update(text="Uninstalling ONNX...")
            os.system("pip uninstall onnxruntime -y")
            loadingWindow.update(text="Installing ONNX GPU...")
            os.system("pip install onnxruntime-gpu")
        else:
            loadingWindow.update(text="Uninstalling ONNX GPU...")
            os.system("pip uninstall onnxruntime-gpu -y")
            loadingWindow.update(text="Installing ONNX...")
            os.system("pip install onnxruntime")
            
    settings.CreateSettings("SwitchLaneDetectionDevice", "switchTo", None)

def CheckLastKnownVersion():
    lastVersion = settings.GetSettings("User Interface", "version")
    if lastVersion == None:
        settings.UpdateSettings("User Interface", "version", variables.VERSION)
        mainUI.switchSelectedPlugin("plugins.Changelog.main")
        return
    
    if lastVersion != variables.VERSION:
        settings.UpdateSettings("User Interface", "version", variables.VERSION)
        mainUI.switchSelectedPlugin("plugins.Changelog.main")
        return
    
def CloseAllPlugins():
    for plugin in pluginObjects:
        plugin.onDisable()
        del plugin
        

timesLoaded = 0
def LoadApplication():
    global mainUI
    global uiUpdateRate
    global loadingWindow
    global timesLoaded

    loadingWindow = loading.LoadingWindow("Please wait initializing...")
    
    if timesLoaded > 0:
        try:
            mainUI.DeleteRoot()
            del mainUI
            import src.mainUI as mainUI
            mainUI.CreateRoot()
        except:
            pass
        
    timesLoaded += 1
        

    CheckForONNXRuntimeChange()

    # Check for new plugin installs
    InstallPlugins()
    
    # Load all plugins 
    loadingWindow.update(text="Loading plugins...")
    GetEnabledPlugins()
    FindPlugins()
    loadingWindow.update(text="Initializing plugins...")
    RunOnEnable()

    logger.printDebug = settings.GetSettings("logger", "debug")
    if logger.printDebug == None:
        logger.printDebug = False
        settings.CreateSettings("logger", "debug", False)

    # We've loaded all necessary modules
    showCopyrightInTitlebar = settings.GetSettings("User Interface", "TitleCopyright")
    if showCopyrightInTitlebar == None:
        settings.CreateSettings("User Interface", "TitleCopyright", True)
        showCopyrightInTitlebar = True
    
    mainUI.titlePath = "- " + open(settings.currentProfile, "r").readline().replace("\n", "") + " "
    mainUI.UpdateTitle()
    mainUI.root.update()
    mainUI.drawButtons()

    loadingWindow.destroy()
    del loadingWindow

    uiUpdateRate = settings.GetSettings("User Interface", "updateRate")
    if uiUpdateRate == None: 
        uiUpdateRate = 0
        settings.CreateSettings("User Interface", "updateRate", 0)

    CheckLastKnownVersion()
    # Show the root window
    mainUI.root.deiconify()

LoadApplication()

data = {}
uiFrameTimer = 0
if __name__ == "__main__":
    while True:
        # Main Application Loop
        try:
            
            allStart = time.time()
            
            # Remove "last" from the data and set it as this frame's "last"
            try: 
                data.pop("last")
                data = {
                    "last": data, 
                    "executionTimes": {}
                }
            except Exception as ex:
                data = {
                    "last": {},
                    "executionTimes": {}
                }  
            
            if variables.RELOADPLUGINS:
                print("Reloading plugins...")
                ReloadPluginCode()
                RunOnEnable()
                variables.RELOADPLUGINS = False
                variables.RELOAD = False # Already reloaded
            
            if variables.RELOAD:
                print("Reloading application...")
                # Reset the open tabs
                settings.UpdateSettings("User Interface", "OpenTabs", [])
                LoadApplication()
                variables.RELOAD = False
            
            # Update the input manager.
            controlsStartTime = time.time()
            data = controls.plugin(data)
            controlsEndTime = time.time()
            data["executionTimes"]["Control callbacks"] = controlsEndTime - controlsStartTime
            
            try:
                if variables.APPENDDATANEXTFRAME != None or variables.APPENDDATANEXTFRAME != [] or variables.APPENDDATANEXTFRAME != {} or variables.APPENDDATANEXTFRAME != "":
                    # Merge the two dictionaries
                    data.update(variables.APPENDDATANEXTFRAME)
                    variables.APPENDDATANEXTFRAME = None
            except: pass
            
            # Enable / Disable the main loop
            if variables.ENABLELOOP == False:
                start = time.time()
                mainUI.update(data)
                end = time.time()
                data["executionTimes"]["UI"] = end - start
                allEnd = time.time()
                data["executionTimes"]["all"] = allEnd - allStart
                try:
                    cv2.destroyWindow("Lane Assist")
                except:
                    pass
                try:
                    cv2.destroyWindow('Traffic Light Detection - B/W')
                except:
                    pass
                try:
                    cv2.destroyWindow('Traffic Light Detection - Red/Green')
                except:
                    pass
                try:
                    cv2.destroyWindow('Traffic Light Detection - Final')
                except:
                    pass
                try:
                    cv2.destroyWindow('TruckStats')
                except:
                    pass
                continue
            
            if variables.UPDATEPLUGINS:
                GetEnabledPlugins()
                FindPlugins()
                variables.UPDATEPLUGINS = False
            
            data = UpdatePlugins("before image capture", data)
            data = UpdatePlugins("image capture", data)
            
            data = UpdatePlugins("before lane detection", data)
            data = UpdatePlugins("lane detection", data)
            
            data = UpdatePlugins("before controller", data)
            data = UpdatePlugins("controller", data)
            
            data = UpdatePlugins("before game", data)
            data = UpdatePlugins("game", data)
            
            data = UpdatePlugins("before UI", data)
            
            # Calculate the execution time of the UI
            start = time.time()
            uiFrameTimer += 1
            if uiFrameTimer > uiUpdateRate:
                mainUI.update(data)
                uiFrameTimer = 0
            end = time.time()
            data["executionTimes"]["UI"] = end - start
            
            data = UpdatePlugins("last", data)
            
            # And then the entire app
            allEnd = time.time()
            data["executionTimes"]["all"] = allEnd - allStart

        
        except Exception as ex:
            try:
                if settings.GetSettings("User Interface", "hide_console") == True:
                    win32gui.ShowWindow(variables.CONSOLENAME, win32con.SW_RESTORE)
            except:
                pass
            if ex.args != ('The main window has been closed.', 'If you closed the app this is normal.'):
                import keyboard
                # Press the F1 key to pause the game
                keyboard.press_and_release("F1")
                from tkinter import messagebox
                import traceback
                exc = traceback.format_exc()
                traceback.print_exc()
                # Pack everything in ex.args into one string
                if not messagebox.askretrycancel("Error", translator.Translate("The application has encountered an error in the main thread!\nPlease either retry execution or close the application (cancel)!\n\n") + exc):
                    break
                else:
                    pass
            else:
                CloseAllPlugins()
                try:
                    if settings.GetSettings("User Interface", "hide_console") == True:
                        import ctypes
                        ctypes.windll.user32.PostMessageW(variables.CONSOLENAME, 0x10, 0, 0)
                except:
                    print("Failed to close console!")
                break
