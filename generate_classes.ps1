#!/usr/bin/env pwsh

#
# This powershell script is NOT for any release, and has no end-user value.
#

Set-StrictMode -Version Latest


$WORKFLOWS_ALL = @(
    "comfyui_default",
    "flux_1.0",
    "flux_neg_1.0",
    "img2img_sdxl_0.3",
    "inpainting_sdxl_0.4",
    "sytan_sdxl_1.0"
)

$WORKFLOWS_FLUX = @(
    "flux_1.0",
    "flux_neg_1.0"
)

$GENERATORS_ALL = @(
    "generate_node_accessor.py"
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
        $api_jsons_map.add($workflow,"{0}_workflow_api.json" -f $workflow)
    }
    return $api_jsons_map
}

function Generate-Classes([String] $generator, [string[]]$SubjectWorkflows) {
    $wfmap = Get-APIJsonsMap($SubjectWorkflows)
    foreach ($workflow in $SubjectWorkflows) {
        python $generator $wfmap[$workflow]
    }
}

Set-Python 11  # local profile  function that sets environment variables for the specified Python 3 version.
$ENV:PYTHONPATH=$PSScriptRoot

foreach($generator_name in @("generate_inputs_dialog.py")){
    $generator = Join-Path -Path $PSScriptRoot -ChildPath "workflow" -AdditionalChildPath @($generator_name)
#   Generate-Classes $generator $WORKFLOWS_ALL
#   Generate-Classes $generator @("sytan_sdxl_1.0")
    Generate-Classes $generator $WORKFLOWS_FLUX
}

# Test with
# Remove-Item $ENV:TEMP\GimpComfyUI_logfile.txt; gimp3 "M:\stills\A_I\misc\example.png" "M:\stills\A_I\misc\1962_TR3B_scaled.png" "M:\stills\A_I\misc\1962_TR3B_mask_scaled.png" "M:\stills\A_I\misc\Kuo-toa_05.png"
# or
# rm -f $TMPDIR/GimpComfyUI_logfile.txt; gimp3 ~/Pictures/example.png ~/Pictures/1962_TR3B_scaled.png ~/Pictures/1962_TR3B_mask_scaled.png  ~/Pictures/Kuo-toa_05.png
