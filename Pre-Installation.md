
# Pre-Installation (optional)
The Pythons included in versions of GIMP are subsets of a "full" python installation. This is very reasonable, but
inconvenient for GimpComfyUI. In particular, they are missing the modules "websocket-client", and "requests-toolbelt".
GIMP pythons are also missing "pip", the tool to manage python modules. Finally, the python modules that *are* included
are often out-of-date, with bugs, obsolete stuff, and security issues. On Windows and Mac, all of these could be mitigated
by pre-installation steps. However, on Linux, the embedded Python is customized to the point that it cannot be user-updated.
To maintain compatibility between platforms, GimpComfyUI embeds the modules "requests", "requests-toolbox", and
"websocket-client". If these modules are also included in GIMP Python, GIMP's modules will be ignored. Furthermore, 
unless bugs or security vulnerabilities are published for GimpComfyUI's embedded modules, they will not be updated.

However, on Windows and Mac, you still might get some benefit from updating some of the OTHER modules included in GIMP's
python. This document outlines how that can be done.
## Windows
You will need to find the folder where GIMP-2.99 or GIMP-3.0 is installed. For most users, as of 2024, Sept 5, that is
"C:\Program Files\Gimp-2.99.18" but you might have it installed somewhere else, and the version may change. In
particular, if GIMP is installed as a "Per-User Application", you will find it under
"C:\Users\<your username>\AppData\Local\Programs".
Open the folders all the way down to &lt;bla&gt;\\&lt;bla&gt;\Gimp-?.??.??\bin, and find the python executable files. On Windows,
as of 2024, Sept 5, the file you are looking for is "python3.11", and the ".exe" on the end is probably hidden. "python3.11"
*might* be updated to something else, that's what you are trying to verify. Once you are certain of the complete directory
path to the exact filename, you are set to continue. If you don't know, it will probably look something like
"C:\Program Files\Gimp-2.99.18\bin\python3.11.exe" or
"C:\Users\<your username>\AppData\Local\Programs\Gimp-2.99.18\bin\python3.11.exe"


Now, you will need to edit the pre-install_windows.ps1 file, and change the lines near the top to the path you figured out above:
* $GIMP_PYTHON_3_11 = "C:\Program Files\Gimp-2.99.18\bin\python3.11.exe"
* $GIMP_PYTHON_3_11_BIN = "C:\Program Files\Gimp-2.99.18\bin"

Don't omit the quotes!

Now, open a terminal, and navigate to this repository. In this dir, run the command ".\pre-install_windows.ps1"
The pre-installer might print some optional instructions. You can now run the installer with GIMP's python, or your system's full python.
## Linux
On Linux, users cannot update GIMP's python modules. 
## Mac
You will need to find the folder where GIMP-2.99 or GIMP-3.0 is installed.
Right-Click on the Gimp-2.99 icon, and select "Open in finder". Then right-click "Show Package Contents". Open the
folders down to Contents\MacOS, and find the python executable files. On Mac, as of 2024, Sept 6, the file you are
looking for is "python3.10". "python3.10" might be (hopefully has!) be updated to something else, that's what you are
trying to verify. Once you are certain of complete directory path to the exact filename, you are set to continue. If you
don't know, it will look something like "/Applications/GIMP.app/Contents/MacOS/python3.10". While right-clicking the
python-executable, you can hold down the clover/option key, and select "Copy &lt;bla&gt; as Pathname".

Now, you will need to edit the pre-install_macos.sh file, and change the lines near the top to the path you figured out above:
* export GIMP_PYTHON_3_10="/Applications/GIMP.app/Contents/MacOS/python3.10"
* export GIMP_PYTHON_3_10_HOME="/Applications/GIMP.app/Contents/MacOS"

Now you need to find the GIMP_PYTHON_3_10_BIN directory. As of 2024, Sept 5, it should be
"/Applications/GIMP.app/Contents/Resources/Library/Frameworks/Python.framework/Versions/3.10/bin"
but you should check this, and verify that "bin" contains files like "normalizer" "python3.10" and "wheel".
Once verified, you can right-click the "bin" folder, hold down the clover/option key, and select "Copy bin as Pathname".
Paste it as the value:
* export GIMP_PYTHON_3_10_BIN="/Applications/GIMP.app/Contents/Resources/Library/Frameworks/Python.framework/Versions/3.10/bin"

Don't omit the quotes!

Now, open a terminal, and navigate to this repository. In this dir, run the command "./pre-install_macos.sh"
The pre-installer might print some optional instructions. You can now run the installer with GIMP's python, or your system's full python.
