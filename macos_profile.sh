#!/usr/bin/env bash

set -e
set -u

# Required. You must set these values correctly for this script to work. The current values worked on macOS Monterey for GIMP 2.99 and 3.0-RC1
export PYTHON_GIMP_3_10_BIN="/Applications/GIMP.app/Contents/Resources/Library/Frameworks/Python.framework/Versions/3.10/bin"
export PYTHON_GIMP_3_10_HOME="/Applications/GIMP.app/Contents/MacOS"
export PYTHON_GIMP_3_10="/Applications/GIMP.app/Contents/MacOS/python3.10"
export PYTHON_SYS_3_10="/Applications/GIMP.app/Contents/Resources/Library/Frameworks/Python.framework/Versions/3.10/Resources/Python.app/Contents/MacOS/Python"

# Background constants. Mostly for reference and future functionality, but you should update to match your system
export PYTHON_GIMP_3_10_PATH=(
    "/Applications/GIMP.app/Contents/Resources/Library/Frameworks/Python.framework/Versions/3.10/lib/python310.zip"
    "/Applications/GIMP.app/Contents/Resources/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10"
    "/Applications/GIMP.app/Contents/Resources/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/lib-dynload"
    "/Applications/GIMP.app/Contents/Resources/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages"
)
export PYTHON_GIMP_3_10_SITE_PACKAGES="/Applications/GIMP.app/Contents/Resources/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages"
#  https://techoverflow.net/2021/02/06/how-to-fix-python-websocket-typeerror-__init__-missing-3-required-positional-arguments-environ-socket-and-rfile/

export IMAGES_4_GIMP=(
        "$HOME/Pictures/example.png"
        "$HOME/Pictures/1962_TR3B_mask_scaled.png"
        "$HOME/Pictures/1962_TR3B_scaled.png"
        "$HOME/Pictures/Kuo-toa_05.png"
    )
export SD_DATA_DIR=$TMPDIR
export GIMP_PLUGINS_DIR="$HOME/Library/Application Support/GIMP/3.0/plug-ins"
export COMFY_CUSTOM_NODES_DIR="$SD_DATA_DIR""custom_nodes"

function gimp3t(){
    /Applications/GIMP.app/Contents/MacOS/gimp --console-messages --verbose ${IMAGES_4_GIMP[*]}
}

function gcui_clear(){
    rm -fv "$TMPDIR/GimpComfyUI_logfile.txt"
}

function gcui_log(){
    less "$TMPDIR/GimpComfyUI_logfile.txt" 
}
function gcui_tail(){
    tail -f "$TMPDIR/GimpComfyUI_logfile.txt" 
}

# MacOS:
mkdir -pv "$SD_DATA_DIR"
mkdir -pv "$SD_DATA_DIR""/models"
mkdir -pv "$COMFY_CUSTOM_NODES_DIR"

# GCUI_REPO="$(dirname "$(readlink -f "$0")")"
 GCUI_REPO="$HOME/projects/hymerfania/gimp_plugins/three_zero/gimp_comfyui"
export GCUI_REPO


INSTALLER_CMD_LITERAL='"$PYTHON_SYS_3_10 $GCUI_REPO/installer.py --gimp_plugins_dir "$GIMP_PLUGINS_DIR" --stable_diffusion_data_dir $SD_DATA_DIR --comfyui_custom_nodes_dir $COMFY_CUSTOM_NODES_DIR"'
INSTALLER_CMD="$PYTHON_SYS_3_10 $GCUI_REPO/installer.py --gimp_plugins_dir $GIMP_PLUGINS_DIR --stable_diffusion_data_dir $SD_DATA_DIR --comfyui_custom_nodes_dir $COMFY_CUSTOM_NODES_DIR"

echo "You should now be able to run this installer in cli-mode, but the GUI will not work. To test the cli, try pasting the text we just loaded into the clipboard."
echo "When ready to actually install, you will need to choose and specify the correct --gimp_plugins_dir."
echo "On macOS Monterey, GIMP 3.0-RC1, a working value for --gimp_plugins_dir is"
echo "   \"$HOME/Library/Application Support/GIMP/3.0/plug-ins\""
echo "This WILL change, at least when GIMP is updated."
echo -e "On systems without local ComfyUI, the temporary directories for stable_diffusion_data_dir and comfyui_custom_nodes_dir will allow the installer to run.\n\n"
echo "$INSTALLER_CMD_LITERAL"
echo -n "$INSTALLER_CMD" | pbcopy
