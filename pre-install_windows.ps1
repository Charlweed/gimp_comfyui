#!/usr/bin/env pwsh
# As of 2024, Aug 28, there remain several 3.10 packages/modules that pip fails to update...
# .. for Microsoft Windows 10 Pro
# OS Name:                   Microsoft Windows 10 Pro
# OS Version:                10.0.19045 N/A Build 19045
# pycairo
# PyGObject

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$PSNativeCommandUseErrorActionPreference = $true # might be true by default

# Required. You must set these values correctly for this script to work.
# On Windows, it's most common to install Gimp in "C:\Program Files" instead of "L:\bin\gimp" like I do.
# But "C:\Program Files" requires administrator priviledges, and has many, MANY other tiersome issues.
$GIMP_PYTHON_3_11 = "L:\bin\gimp\GIMP-2.99.18\bin\python3.11.exe"
$GIMP_PYTHON_3_11_BIN = "L:\bin\gimp\GIMP-2.99.18\bin"
$GIMP_PYTHON_3_11_HOME = "L:\bin\gimp\GIMP-2.99.18\bin"

# Background constants. Mostly for reference and future functionality, but you should update to match your system
$GIMP_PYTHON_3_11_PATH = (
    "L:\bin\gimp\GIMP-2.99.18\lib\python311.zip",
    "L:\bin\gimp\GIMP-2.99.18\lib\python3.11",
    "L:\bin\gimp\GIMP-2.99.18\lib\python3.11\lib-dynload",
    "C:\Users\chymes\.local\lib\python3.11-mingw_x86_64\site-packages",
    "L:\bin\gimp\GIMP-2.99.18\lib\python3.11\site-packages"
)
$GIMP_PYTHON_3_11_SITE_PACKAGES = "L:\bin\gimp\GIMP-2.99.18\lib\python3.11\site-packages"

# Assign the path, so that pip will update Gimp's python and not the default python
$ENV:PATH = "$GIMP_PYTHON_3_11_HOME;$ENV:PATH"

# Get the pip bootstrap script..
# Linux
# wget -O $ENV:TMP/get-pip.py https://bootstrap.pypa.io/get-pip.py
# macOS
# curl  https://bootstrap.pypa.io/get-pip.py -o $ENV:TMP/get-pip.py
# Windows
Invoke-WebRequest -OutFile $ENV:TMP/get-pip.py https://bootstrap.pypa.io/get-pip.py

# Run the pip bootstrap script.
& $GIMP_PYTHON_3_11 $ENV:TMP/get-pip.py

# Update pip from it's home.
& $GIMP_PYTHON_3_11 -m ensurepip --upgrade


# On some systems, a package named "websocket" conflicts the the required package "websocket-client"
pip uninstall websocket # On macOS python 3.10, this is websocket-0.2.1, the built-in, old, low-level module. It is NOT used by GimpComfyUI
pip install websocket-client # This is a newer, mid-level module. It is required by GimpComfyUI.
pip install requests-toolbelt # Required to upload images.
pip install tk  # Enables python dialogs, choosers, etc..

# We are explicit here, so we can examine and manipulate the intermediate files.
# List the outdated packages to a JSON file.
pip --disable-pip-version-check list --outdated --format=json > $ENV:TMP/outdated_python_modules.json
# Convert the JSON file to a plain list.
Get-Content $ENV:TMP/outdated_python_modules.json | & $GIMP_PYTHON_3_11 -c "import json, sys; print('\n'.join([x['name'] for x in json.load(sys.stdin)]))"  > $ENV:TMP/outdated_python_modules.txt

# Attempt to update each module. Beware doing this for anything else then Gimp's python.
# As noted above, some packages will not correctly install or update. You can ignore most errors, and work without Tkinter.
$ErrorActionPreference = "Continue"
[string[]]$outdated_modules = Get-Content $ENV:TMP/outdated_python_modules.txt
$outdated_modules

foreach ($module_name in $outdated_modules) {
    pip install -U $module_name
}

# Windows:
New-Item -ItemType Directory -Path $ENV:TMP\gimp_scripts
New-Item -ItemType Directory -Path $ENV:TMP\stable_diffusion\models
New-Item -ItemType Directory -Path $ENV:TMP\stable_diffusion\custom_nodes
$ENV:GCUI_REPO=$PSScriptRoot
# The separator inconsistancies are because the command is executed by the shell, but the arguments are parsed by python
$INSTALLER_CMD="$ENV:GCUI_REPO\installer.py --gimp_scripts_dir $ENV:TMP/gimp_scripts --stable_diffusion_data_dir $ENV:TMP/stable_diffusion --comfyui_custom_nodes_dir $ENV:TMP/stable_diffusion/custom_nodes"
$InformationPreference="Continue"

Write-Information "You should now be able to run the installer. To test the cli, try pasting the text we just loaded into the clipboard."
Write-Information "When ready to actually install, you will need to choose and specify the correct --gimp_scripts_dir."
Write-Information "On Windows, Gimp 2.99, a working value for --gimp_scripts_dir is"
Write-Information "`"~/AppData/Roaming/Gimp/2.99/plug-ins`""
Write-Information "This WILL change, at least when Gimp is updated."
Write-Information "On systems without local ComfyUI, the temporary directories for stable_diffusion_data_dir and comfyui_custom_nodes_dir will allow the installer to run.`n`n"
Write-Information "$INSTALLER_CMD"
Write-Information "$INSTALLER_CMD" | clip
