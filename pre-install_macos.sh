#!/usr/bin/env bash
# As of 2024, Sep 5, there remain several 3.10 packages/modules that pip fails to install or update...
# .. for macOS Monterey
# ProductName:	macOS
# ProductVersion:	12.7.6
# BuildVersion:	21H1320
# packaging
# pycairo
# PyGObject
# pyproject-hooks
# Tk/Tkinter

set -e
set -u

# Required. You must set these values correctly for this script to work. The current values worked on macOS Monterey for Gimp 2.99
export GIMP_PYTHON_3_10="/Applications/GIMP.app/Contents/MacOS/python3.10"
export GIMP_PYTHON_3_10_HOME="/Applications/GIMP.app/Contents/MacOS"
export GIMP_PYTHON_3_10_BIN="/Applications/GIMP.app/Contents/Resources/Library/Frameworks/Python.framework/Versions/3.10/bin"

# Background constants. Mostly for reference and future functionality, but you should update to match your system
export GIMP_PYTHON_3_10_PATH=(
    "/Applications/GIMP.app/Contents/Resources/Library/Frameworks/Python.framework/Versions/3.10/lib/python310.zip"
    "/Applications/GIMP.app/Contents/Resources/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10"
    "/Applications/GIMP.app/Contents/Resources/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/lib-dynload"
    "/Applications/GIMP.app/Contents/Resources/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages"
)
export GIMP_PYTHON_3_10_SITE_PACKAGES="/Applications/GIMP.app/Contents/Resources/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages"
#  https://techoverflow.net/2021/02/06/how-to-fix-python-websocket-typeerror-__init__-missing-3-required-positional-arguments-environ-socket-and-rfile/

# Assign the path, so that pip will update Gimp's python and not the default python
PATH="$GIMP_PYTHON_3_10_HOME:$GIMP_PYTHON_3_10_BIN:$PATH"
export PATH

# Get the pip bootstrap script..
# Linux
# wget -O $TMPDIR/get-pip.py https://bootstrap.pypa.io/get-pip.py
# macOS
curl  https://bootstrap.pypa.io/get-pip.py -o "$TMPDIR/get-pip.py"
chmod a+rx "$TMPDIR/get-pip.py"
# Windows
# Invoke-WebRequest -OutFile $ENV:TMP/get-pip.py https://bootstrap.pypa.io/get-pip.py

# Run the pip bootstrap script. Should have no need for sudo
$GIMP_PYTHON_3_10 "$TMPDIR/get-pip.py"

# Update pip from its home.
$GIMP_PYTHON_3_10 -m ensurepip --upgrade


# On some systems, a package named "websocket" conflicts the the required package "websocket-client"
pip uninstall websocket # On macOS python 3.10, this is websocket-0.2.1, the built-in, old, low-level module. It is NOT used by GimpComfyUI
pip install websocket-client # This is a newer, mid-level module. It is required by GimpComfyUI.
pip install requests-toolbelt # Required to upload images.
pip install tk  # SHOULD enable python dialogs, choosers, etc., but does not work on macOS Gimp's python 3.10

# We are explicit here, so we can examine and manipulate the intermediate files.
# List the outdated packages to a JSON file.
pip --disable-pip-version-check list --outdated --format=json > "$TMPDIR/outdated_python_modules.json"
# Convert the JSON file to a plain list.
cat "$TMPDIR/outdated_python_modules.json" | $GIMP_PYTHON_3_10 -c "import json, sys; print('\n'.join([x['name'] for x in json.load(sys.stdin)]))"  > "$TMPDIR/outdated_python_modules.txt"

# Attempt to update each module. Beware doing this for anything else then Gimp's python.
# As noted above, some packages will not correctly install or update. You can ignore most errors, and work without Tkinter.
set +e
cat "$TMPDIR/outdated_python_modules.txt" | xargs -n1 pip install -U

# MacOS:
mkdir -p "$TMPDIR/gimp_plugins"
mkdir -p "$TMPDIR/stable_diffusion/models"
mkdir -p "$TMPDIR/stable_diffusion/custom_nodes"
GCUI_REPO="$(dirname "$(readlink -f "$0")")"
export GCUI_REPO
INSTALLER_CMD="/Applications/GIMP.app/Contents/MacOS/python3.10 $GCUI_REPO/installer.py --gimp_plugins_dir $TMPDIR/gimp_plugins --stable_diffusion_data_dir $TMPDIR/stable_diffusion --comfyui_custom_nodes_dir $TMPDIR/stable_diffusion/custom_nodes"

echo "You should now be able to run this installer in cli-mode, but the GUI will not work. To test the cli, try pasting the text we just loaded into the clipboard."
echo "When ready to actually install, you will need to choose and specify the correct --gimp_plugins_dir."
echo "On macOS Monterey, Gimp 2.99, a working value for --gimp_plugins_dir is"
echo "   \"~/Library/Application Support/GIMP/2.99/plug-ins\""
echo "This WILL change, at least when Gimp is updated."
echo -e "On systems without local ComfyUI, the temporary directories for stable_diffusion_data_dir and comfyui_custom_nodes_dir will allow the installer to run.\n\n"
echo "$INSTALLER_CMD"
echo -n "$INSTALLER_CMD" | pbcopy
