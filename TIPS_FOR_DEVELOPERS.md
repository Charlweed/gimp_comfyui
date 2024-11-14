# Tips for developers

Unlike end users, developers will needs to frequently wipe, re-install, and repeatedly launch gimp and ComfyUI. This is best done with command-line tools, variables, and some scripting.

### Windows Powershell
You can customize, and then "dot source" the `windows_profile.ps1` file, to automate tasks.
### Mac bash
You can customize, and then source the `macos_profile.sh` file, to automate tasks.
## Running the installer
After sourcing the profile for your platform, you can echo the value of the `$INSTALLER_CMD` variable for pasting into your shell.
You can customize it in the profile, or after pasting it.
## Running and testing in Gimp
After sourcing the profile for your platform, there will be a shell function `gimp3t` that you can run from your shell. It will start GIMP in verbose mode.

NOTE: The GimpComfyUI plug-in prints to a log file. It is in your temporary directory, named `GimpComfyUI_logfile.txt` If the plugin fails to load and start, the log file will NOT be written. Often, that's because a reference cannot be resolved in python. The `GimpComfyUI_logfile.txt`is very useful to see progress, and of course to see errors.

## Generating classes with powershell
[See ./ADDING_WORKFLOWS.md](ADDING_WORKFLOWS.md)
## Running ComfyUI
Remember that a ComfyUI must be accessible for GimpComfyUI to function.
As of this writing (2024/11/13), if you want to run ComfyUI on a *desktop* PC with a x090 Nvidia video card, the Windows drivers offer huge performance advantages over the Linux drivers, and there are no available drivers for Apple computers. Complain to Nvidia.

This stinks, because it means desktop users are stuck with running a python server on Windows. Windows python has significant issues in security, compatibility, and ironically, non-graphics performance. You can expect these issues will never be addressed, because they have been tracked and not fixed for decades. Complain to Microsoft.

Comfy.org has a CLI package that improves the User Experience of running ComfyUI. It is oriented for "managing" ComfyUI for server users, and is entirely in python. For me, it is not very handy for plug-in or node development, but it might be great for you. I have my own scripting to easily start and stop ComfyUI, I might put it into a gist.

Anyway, you will want to run ComfyUI with the "--listen" and "--verbose" arguments, and keep a terminal open for it. You will want to see if GimpComfyUI is posting an invalid prompt, and you will want to see progress through the workflow nodes.

When you update ComfyUI, you might find that changes to the built-in nodes break the workflow_api that GimpComfyUI uses. [See ./ADDING_WORKFLOWS.md](ADDING_WORKFLOWS.md)

