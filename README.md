# Welcome to GimpComfyUI

**GimpComfyUI** is a GIMP plugin to connect near-realtime image editing to AI image generation via ComfyUI's web api.
It enables GIMP to connect directly to ComfyUI, and optionally send a layer
as an image as you edit it. This plugin is targeted for GIMP 3.0, which is not yet released, but 
is scheduled for release in 2024. The current development and testing platform is GIMP 2.99+

NOTE: This project is an unstable alpha version, and GIMP 3 is also pre-release. Your Mileage May Vary.

# Prerequisites and Dependencies
- GIMP 2.99.18+ development release, or GIMP 3.0.x when it becomes available.
- Python 3.10+ to run the "installer". This could be the same python used to run ComfyUI, or the python built into GIMP,
 but a standalone full python is preferred. Anyway, it should be on your terminal's PATH when you run the installer, or
 you should know the full path to the python executable.
- Access to ComfyUI via a stable URL. The preferred scenario is that the latest stable version of ComfyUI is installed
 on your local host.
- To install ImageTransceiver-ComfyUI, you will need write access to ComfyUI's "custom_nodes" folder. Support for
comfy-org's Node Registry is under development.
- You can optionally clone the ImageTransceiver-ComfyUI project. See "Cloning" below.
- Have ComfyUI running and reachable when you use this plugin! The plugin checks connectivity whenever you invoke a 
procedure. **If GimpComfyUI cannot connect to ComfyUI, it will fail, and the only indication will be in the logs**.


ComfyUI's API is very workflow dependent. Any GIMP plug-in for ComfyUI will basically only work for a particular
api-style workflow and its nodes. Installing 3rd party nodes and workflows is currently out-of-scope of this project,
but the following workflows are available as assets in the "./assets" directory:
- comfyui_default_workflow
- comfyui_default_workflow_api
- img2img_sdxl_0.3_workflow
- img2img_sdxl_0.3_workflow_api
- inpainting_sdxl_0.4_workflow
- inpainting_sdxl_0.4_workflow_api
- sytan_sdxl_1.0_workflow
- sytan_sdxl_1.0_workflow_api
- Various Flux workflows are under development.

# Cloning
It is not a good idea to clone or copy this entire repository into the plug-ins folder, because GIMP will read every
file, and try to evaluate each as plug-in content. This raises security and performance issues.

There is no need to clone the ImageTransceiver-ComfyUI project, but If you wish to review or modify the code of the 
ImageTransceiver-ComfyUI node, you can clone it into a local directory, and change the `COMFY_NODE_PROJ` URL in the 
installer.py script from a GitHub url to a local protocol url. For example, you can change:

`COMFY_NODE_PROJ: "https://github.com/Charlweed/image_transceiver`

to

`COMFY_NODE_PROJ: "file://L:/projects/comfyui_custom_nodes/image_transceiver"`

# Building
There is no need to build anything.

# Installation
This project includes a rudimentary installer. It has these basic functions:
- Configure the foundational JSON files with data about your GIMP, StableDiffusion, and ComfyUI setups.
- Copy the GIMP plugin to the GIMP user's "plug-ins" folder.
- Download, extract, and copy the ComfyUI custom node to a specified folder.

The basic config data may be specified from the command line, or a TK GUI, if a GUI is available in your Python. For 
destinations, You might first choose any reasonable destinations, and then later manually move the files from there into
final folders yourself.

The installer.py script is in the root of this project directory. It is best launched from the command line, and has
"optional" options: "--gimp_scripts_dir" "--stable_diffusion_data_dir" and "--comfyui_custom_nodes_dir". If you do not 
use these options, the installer will try to open a TK directory chooser. Failing that, the installer will prompt you 
type in both values. **If you don't launch the installer from the command line, and your python cannot access TK, the 
installer will seem to silently fail**.

For GIMP 2.99, the plug-ins is folders are platform-dependent, for example:
`~/AppData/Roaming/Gimp/2.99/plug-ins/Gimp-comfyui` or `~/.config/Gimp/2.99/plug-ins/Gimp-comfyui`. For ComfyUI, the
custom node files and folders belong in `<some-parent-path>/ComfyUI/custom_nodes`. The custom node for ComfyUI
is only required for real-time image manipulation. But if you don't install it, you will miss out on a really cool
feature.😄

## Installation steps
Assuming GIMP 2.99 and ComfyUI are installed and working:
1) Locate or choose your GIMP plugins-folder. The folder in your home folder is the simplest choice:
`~/AppData/Roaming/Gimp/2.99/plug-ins` for Windows, or `$HOME/.var/app/org.gimp.GIMP/config/GIMP/2.99/plug-ins` on
linux, `"~/Library/Application Support/GIMP/2.99/plug-ins"` on MacOS. Replace the ~ with your home directory.
2) Locate your ComfyUI folder, and find the `custom_nodes` folder in it.
3) Locate, create, or choose your StableDiffusion data folder, which is the parent dir to `models`. Typically, this will
be `ComfyUI`, the same directory where `custom_nodes` is located, but does not need to be. **It must have a `models`
 sub-directory, so create that if you are using a temporary or dummy directory.**
4) Locate, or choose, an install-time python installation. On Windows and Mac, you can choose the python bundled with
GIMP, but GIMP's python does not have TK installed, so you will need to use the command line 
interface. Linux GIMP's embedded python cannot be used externally.
5) In a terminal/console, execute ``<your-python> <this-project>/installer.py`` if you are providing command-line 
options, put each directory name in quotes, to avoid problems with spaces.

If a dialog opens:
6) Choose your account's GIMP plug-in folder, i.e. ``~/AppData/Roaming/Gimp/2.99/plug-ins`` and click "Ok"
7) Choose the ComfyUI custom_nodes folder, i.e. ``~/projects/3rd_party/ComfyUI/custom_nodes`` and click "Ok"
Even if you do not have a local ComfyUI installed, pick an existing directory, perhaps the temp directory. Otherwise, 
the installer will stop before installing the GIMP plug-in. The Pre-Installation scripts create example temporary 
directories, and prints their location.
8) Choose your StableDiffusion data folder, i.e. `L:/data/stable_diffusion`, or `~/projects/3rd_party/ComfyUI` 
and click "Ok". Again, even if you do not have StableDiffusion nor ComfyUI installed, pick an existing directory.

If a dialog does not open:
6) At the prompt `Please provide an existing directory path for gimp_scripts_dir`, enter your account's GIMP plug-in folder, i.e. ``~/AppData/Roaming/Gimp/2.99/plug-ins`` and press "return"
7) At the prompt `Please provide an existing directory path for comfyui_custom_nodes_dir`, enter the ComfyUI custom_nodes folder, i.e. ``~/projects/3rd_party/ComfyUI/custom_nodes`` and press "return"
8) At the prompt `Please provide an existing directory path for stable_diffusion_data_dir`, enter your StableDiffusion data folder, i.e. `L:/data/stable_diffusion`, or `~/projects/3rd_party/ComfyUI` and press "return"

Installation will proceed and finish.

# After Installation
- On macOS and Linux, **the plug-in and custom node might silently fail if they are not executable.** Ensure the execute 
bit is set on each .py file by running  
`find <plug-in-dir> -iname '*.py' -exec chmod -v a+x {} \;` and
`find <custom-nodes-dir>/image_transceiver -iname '*.py' -exec chmod -v a+x {} \; `
- *Permanently* set the environment variable "STABLE_DIFF_PREF_ROOT" to the parent of your StableDiffusion "models" 
directory. Typically, this will be `<bla-bla>/ComfyUI`, but if you have relocated stuff, you can configure that here. 
If the environment variable STABLE_DIFF_PREF_ROOT is unset, the plugin will use (and create child directories in!) 
"&lt;USERHOME&gt;/data/stable_diffusion/", which is probably not what you want, if you have a local stable diffusion.
The procedure for permanently setting environment variables for your system is out-of-scope of this document.
- Restart ComfyUI, read the logs, and ensure that the Custom node(s) were loaded correctly.
- Restart GIMP, and you will see a GimpComfyUI menu item.
- Configure connection properties via `GimpComfyUI ➳ Config` and set the ComfyUI API connection URL
-- (`http://localhost:8188/` by default) and the ImageTransceiver connection URL (`http://localhost:8765/` by default)


# Usage
Before starting GIMP, start the ComfyUI server.  The plugin checks connectivity whenever you invoke a procedure. **If 
GimpComfyUI cannot connect to ComfyUI, it will fail, and the only indication will be in the logs.** To monitor the 
progress of ComfyUI, it is best to start it in Console mode. This also allows you to watch the console to ensure there 
are no errors.  NOTE: If you are running your own ComfyUI, but on a different host then "localhost", then you need to 
start ComfyUI with the additional option `--listen 0.0.0.0`, otherwise ComfyUI will reject connections from your GIMP 
clients. After starting, the console or logs should show that image_transceiver was loaded. You should see text that
looks like:
```commandline
Import times for custom nodes:
   0.0 seconds: L:\projects\3rd_party\ComfyUI\custom_nodes\image_transceiver
```
There might be additional logging that looks like:
```
[image_transceiver.py:153 -       server_control() ] server_control; Operation ServerOperation.START
```
## ComfyUI
 See the README for the [ImageTransceiver-ComfyUI project](https://github.com/Charlweed/image_transceiver) for
 details on setting-up ComfyUI for live img2img from GIMP.
## GIMP
Start GIMP 2.99.18+ development release, or GIMP 3.0.x.
### Workflow Coupling
Workflow coupling allows you to use a ComfyUI directly from GIMP via settings in GIMP dialogs. It is for situations
where you have a set workflow, and all you want to change are the values for the inputs of that workflow. For example,
this is what the dialog for [Sytan's SDXL workflow](https://github.com/SytanSD/Sytan-SDXL-ComfyUI) looks like in GIMP:


<img alt="GIMP dialog_00" src="./illustrations/gimp_sytan_dialog_00.png" width="512"/>

If you edit the values in the dialog, then click "Apply", ComfyUI will run the workflow, and (eventually) the final
images will open directly within GIMP. If you click "Ok", the dialog will close, and the workflow will run. 
Note that it can take quite a few seconds, even minutes, to run a workflow. You can track the progress in the console
of ComfyUI. 
#### Additional Workflows
Adding a new ConfyUI workflow to couple to GIMP requires some computing and python 3 skills. You need  to complete the
dialog that GIMP opens for the workflow. The difficulty depends upon the size and complexity of the workflow, and the
datatypes that workflow processes.
[Read more here](./adding_workflows.md)


### Live Connections➳Follow-In-ComfyUI
ImageTransceiver-ComfyUI is a custom node that enables GIMP to connect directly to ComfyUI, and send a layer as an image
as you edit it. For best initial results, choose a modestly sized image. Here, we use the 764x764 sketch from 
the img2img ComfyUI demo, so you can see how your painting changes the final results.
You should see the GimpComfyUI menu at the top of the GIMP Window. Insure your main image layer is selected, then
navigate the menus to "GimpComfyUI" ➳ "Live Connections" ➳ "Follow-in-ComfyUI"
<img alt="GIMP dialog_00" src="./illustrations/gimp_menus_00.png" width="512"/>

A daemon dialog will appear. Select the radio button "Queue prompt Automatically":
<img src="./illustrations/daemon_control_01.png" alt="daemon_control_01" width="512" />

Now, you can paint, draw, cut, spray, whatever, into that layer, and the changes will affect what ComfyUI
generates. Sometimes your manipulations will yield exactly what you might expect, often they will not.  All the
prompt-crafting issues are in play, but lower "denoise" strengthens how much the GIMP image comes through to the final
image.

# Known Issues
The python web-socket library on Windows is inexplicably slow, especially for localhost. The dialogs might take seconds
to open on even on the fastest PCs with 64gb RAM, and dozens of processors. You can run ComfyUI on your PC, connect to it 
via your LAN with a Mac (or Linux), and everything will be 4-8 times faster than localhost on the PC. There is no 
available fix as of 2024/08/24. 

# Troubleshooting
- Verify that whatever plugin folder you are using (~/.config/Gimp/2.99/plug-ins) is listed in the GIMP's plug-ins 
- folders. (`Edit➳Preferences➳Folders➳Plug-Ins`)

# Contributing

This is unsupported alpha software, but if you see a problem, or opportunities for improvement, please open an issue and
/or make a pull request.

# License

[MIT](LICENSE)
