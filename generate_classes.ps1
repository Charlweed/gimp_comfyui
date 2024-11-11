#!/usr/bin/env pwsh
# MIT License
# Copyright (c) 2024 Charles Hymes
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# This powershell script is NOT for any release, and has no end-user value.
#
param(
    [Switch]$SkipAccessors,
    [Switch]$SkipDialogs,
    # CAUTION: GenerateGlue will insert glue code for each processed workflow, even if that workflow already
    # has glue code.
    #
    [Switch]$GenerateGlue
)

Set-StrictMode -Version Latest

$WORKFLOWS_ALL = @(
    "comfyui_default",
    "flux_1.0",
    "flux_neg_1.1",
    "flux_neg_upscale_sdxl_0.5",
    "img2img_sdxl_0.3",
    "inpainting_sdxl_0.4",
    "sytan_sdxl_1.0"
)

$WORKFLOWS_FLUX = @(
    "flux_1.0",
    "flux_neg_1.1",
    "flux_neg_upscale_sdxl_0.5"
)

$GENERATORS_ACCESSORS = @(
    "generate_node_accessor.py"
)
$GENERATORS_DIALOGS = @(
    "generate_inputs_dialog.py"
)
$GENERATORS_GLUE = @(
    "generate_inputs_dialog.py"
)

function Get-APIJsons([string[]]$SubjectWorkflows) {
    $api_jsons = @()
    foreach ($workflow in $SubjectWorkflows) {
        $api_jsons += "{0}_workflow_api.json" -f $workflow
    }
    return $api_jsons
}

function Get-APIJsonsMap([string[]]$SubjectWorkflows) {
    $api_jsons_map = @{}
    foreach ($workflow in $SubjectWorkflows) {
        $api_jsons_map.add($workflow, "{0}_workflow_api.json" -f $workflow)
    }
    return $api_jsons_map
}

function Generate-Classes([String] $generator, [string[]]$SubjectWorkflows) {
    $wfmap = Get-APIJsonsMap($SubjectWorkflows)
    foreach ($workflow in $SubjectWorkflows) {
        $json = $wfmap[$workflow]
        python $generator $json
        $failed = $LastExitCode -ne 0
        if ($failed){
            throw "Error running generator `"$generator`" on `"$json`""
        }
    }
}

$GENERATORS = @()
if (-not $SkipAccessors) {
    $GENERATORS += $GENERATORS_ACCESSORS
}
else {
    Write-Warning "Skipping generator $GENERATORS_ACCESSORS"
}
if (-not $SkipDialogs) {
    $GENERATORS += $GENERATORS_DIALOGS
}
else {
    Write-Warning "Skipping generator $GENERATORS_DIALOGS"
}
if ($GenerateGlue) {
    Write-Warning "Inserting glue code into gimp_comfyui.py"
    $GENERATORS += $GENERATORS_GLUE
}

Set-Python 11  # local profile  function that sets environment variables for the specified Python 3 version.
$ENV:PYTHONPATH = $PSScriptRoot

foreach ($generator_name in $GENERATORS) {
    $generator = Join-Path -Path $PSScriptRoot -ChildPath "workflow" -AdditionalChildPath @($generator_name)
    Write-Information "Running generator `"$generator`"" -InformationAction Continue
    Generate-Classes $generator $WORKFLOWS_ALL
#    Generate-Classes $generator $WORKFLOWS_FLUX
}

# Test with
# Remove-Item $ENV:TEMP\GimpComfyUI_logfile.txt; gimp3 "M:\stills\A_I\misc\example.png" "M:\stills\A_I\misc\1962_TR3B_scaled.png" "M:\stills\A_I\misc\1962_TR3B_mask_scaled.png" "M:\stills\A_I\misc\Kuo-toa_05.png"
# or
# rm -f $TMPDIR/GimpComfyUI_logfile.txt; gimp3 ~/Pictures/example.png ~/Pictures/1962_TR3B_scaled.png ~/Pictures/1962_TR3B_mask_scaled.png  ~/Pictures/Kuo-toa_05.png
