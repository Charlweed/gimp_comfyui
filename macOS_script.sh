#!/usr/bin/env bash
export PYTHON_GIMP_3_10="/Applications/GIMP.app/Contents/MacOS/python3.10"
export PYTHON_GIMP_3_10_BIN="/Applications/GIMP.app/Contents/Resources/Library/Frameworks/Python.framework/Versions/3.10/bin"
export PYTHON_GIMP_3_10_HOME="/Applications/GIMP.app/Contents/MacOS"
export PYTHON_SYS_3_10="/Applications/GIMP.app/Contents/Resources/Library/Frameworks/Python.framework/Versions/3.10/Resources/Python.app/Contents/MacOS/Python"
export IMAGES_4_GIMP=(
        "/Users/chymes/Pictures/example.png"
        "/Users/chymes/Pictures/1962_TR3B_mask_scaled.png"
        "/Users/chymes/Pictures/1962_TR3B_scaled.png"
        "/Users/chymes/Pictures/Kuo-toa_05.png"
    )
export SD_DATA_DIR=$TMPDIR
export GIMP_PLUGINS_DIR="/Users/chymes/Library/Application Support/GIMP/3.0/plug-ins"
export COMFY_CUSTOM_NODES_DIR="$SD_DATA_DIR""custom_nodes"

mkdir -pv "$SD_DATA_DIR"
mkdir -pv "$COMFY_CUSTOM_NODES_DIR"

echo "Try ..."
echo "$PYTHON_SYS_3_10" ./installer.py --gimp_plugins_dir \"$GIMP_PLUGINS_DIR\" --stable_diffusion_data_dir \"$SD_DATA_DIR\" --comfyui_custom_nodes_dir \"$COMFY_CUSTOM_NODES_DIR\"
# "$PYTHON_SYS_3_10" ./installer.py --gimp_plugins_dir "$GIMP_PLUGINS_DIR" --stable_diffusion_data_dir "$SD_DATA_DIR" --comfyui_custom_nodes_dir "$COMFY_CUSTOM_NODES_DIR"
