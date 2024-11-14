#!/usr/bin/env pwsh

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$PSNativeCommandUseErrorActionPreference = $true # might be true by default

# Required. You must set these values correctly for this script to work.
# On Windows, it's most common to install GIMP in "C:\Program Files" instead of "L:\bin\gimp" like I do.
# But "C:\Program Files" requires administrator priviledges, and has many, MANY other tiersome issues.
# This is an associative array containing other associative arrays. It allows the Start-Gimp function to
# take the major, minor and patch version as arguments. Just ensure that the path strings are correct for
# Each version for GIMP you have.
# CHANGE THESE FOR YOUR GIMPs:
$global:GIMP_EXEs = @{
    2 = @{
        10 = "L:\bin\gimp\GIMP-2.10.36\bin\gimp-2.10.exe"
        99 = "L:\bin\gimp\GIMP-2.99.18\bin\gimp-2.99.exe"
    }
    3 = @{
        0 = @{
            "RC1" = "L:\bin\gimp\GIMP-3.0-RC1\bin\gimp-3.0.exe"
        }
    }
}
$PYTHON_GIMP_3_11 = "L:\bin\gimp\GIMP-3.0-RC1\bin\python3.11.exe"
$PYTHON_GIMP_3_11_BIN = "L:\bin\gimp\GIMP-3.0-RC1\bin"
$PYTHON_GIMP_3_11_HOME = "L:\bin\gimp\GIMP-3.0-RC1\bin"

# Background constants. Mostly for reference and future functionality, but you should update to match your system
$PYTHON_GIMP_3_11_PATH = (
    "L:\bin\gimp\GIMP-3.0-RC1\lib\python311.zip",
    "L:\bin\gimp\GIMP-3.0-RC1\lib\python3.11",
    "L:\bin\gimp\GIMP-3.0-RC1\lib\python3.11\lib-dynload",
    "C:\Users\luckyuser\.local\lib\python3.11-mingw_x86_64\site-packages",
    "L:\bin\gimp\GIMP-3.0-RC1\lib\python3.11\site-packages"
)
$PYTHON_GIMP_3_11_SITE_PACKAGES = "L:\bin\gimp\GIMP-3.0-RC1\lib\python3.11\site-packages"

$IMAGES_4_GIMP=(
        "M:\stills\A_I\misc\Pictures\example.png",
        "M:\stills\A_I\misc\Pictures\1962_TR3B_mask_scaled.png",
        "M:\stills\A_I\misc\Pictures\1962_TR3B_scaled.png",
        "M:\stills\A_I\misc\Pictures\Kuo-toa_05.png"
    )

function Start-Gimp(
    [Parameter(Mandatory)][int]$MajorVersion,
    [Parameter(Mandatory)][int]$MinorVersion,
    $PatchVersion,
    [Switch] $Quiet,
    [Switch]$DebugGimp,
    [parameter(mandatory = $false, ValueFromRemainingArguments = $true)]$Remaining
) {

    # $gimp_args = @("--console-messages", "--no-fonts", "--no-splash")
    $gimp_args = @("--console-messages", "--no-splash")
    if (($null -ne $Remaining) -and ($Remaining -ne "")) {
        $gimp_args += $Remaining
    }
    $arg_str = ([system.String]::Join(" ", $gimp_args)).trim()
    Write-Output "gimp arguments=`"$arg_str`""

    if (-not $Quiet) {
        $gimp_args += "--verbose"
    }
    if (-not $DebugGimp) {
        if ($Env:DEBUG_GIMP) {
            Remove-Item Env:DEBUG_GIMP
        }
    }
    if ($PatchVersion) {
        Write-Information $GIMP_EXEs[$MajorVersion][$MinorVersion][$PatchVersion] $gimp_args -InformationAction Continue
        & $GIMP_EXEs[$MajorVersion][$MinorVersion][$PatchVersion] $gimp_args
    }
    else {
        Write-Information $GIMP_EXEs[$MajorVersion][$MinorVersion] $gimp_args -InformationAction Continue
        & $GIMP_EXEs[$MajorVersion][$MinorVersion] $gimp_args
    }
}

function Start-Gimp2([Switch] $Quiet,
    [Switch]$DebugGimp,
    [parameter(mandatory = $false, ValueFromRemainingArguments = $true)]$Remaining
) {
    Start-Gimp -MajorVersion 2 -MinorVersion 10 -Quiet:$Quiet -DebugGimp:$DebugGimp -Remaining $Remaining
}

function Start-Gimp3([Switch] $Quiet,
    [Switch]$DebugGimp,
    [parameter(mandatory = $false, ValueFromRemainingArguments = $true)]$Remaining
) {
    Start-Gimp -MajorVersion 3 -MinorVersion 0 -PatchVersion "RC1" -Quiet:$Quiet -DebugGimp:$DebugGimp -Remaining $Remaining
}

function gimp3t() {
    Start-Gimp3 -DebugGimp $IMAGES_4_GIMP
}

# CHANGE THESE FOR YOUR GIMP:
New-Item -ItemType Directory -Path $ENV:TMP\gimp_plugins
New-Item -ItemType Directory -Path $ENV:TMP\stable_diffusion\models
New-Item -ItemType Directory -Path $ENV:TMP\stable_diffusion\custom_nodes
$ENV:GCUI_REPO=$PSScriptRoot
# The separator inconsistencies are because the command is executed by the shell, but the arguments are parsed by python
$INSTALLER_CMD="$ENV:GCUI_REPO\installer.py --gimp_plugins_dir $ENV:TMP/gimp_plugins --stable_diffusion_data_dir $ENV:TMP/stable_diffusion --comfyui_custom_nodes_dir $ENV:TMP/stable_diffusion/custom_nodes"
$InformationPreference="Continue"

Write-Information "You should now be able to run the installer. To test the cli, try pasting the text we just loaded into the clipboard."
Write-Information "When ready to actually install, you will need to choose and specify the correct --gimp_plugins_dir."
Write-Information "On Windows, GIMP 3.0, a working value for --gimp_plugins_dir is"
Write-Information "`"~/AppData/Roaming/Gimp/3.0/plug-ins`""
Write-Information "This WILL change, at least when GIMP is updated."
Write-Information "On systems without local ComfyUI, the temporary directories for stable_diffusion_data_dir and comfyui_custom_nodes_dir will allow the installer to run.`n`n"
Write-Information "$INSTALLER_CMD"
Write-Information "$INSTALLER_CMD" | clip
