Hi Robin, you asked for a use-case for an "exclude" feature for the node-publish utility. Here's a rough one:
# Feature:
An `exclude:` key-value pair in the `publish.yml` file that specifies files and directories in the git project folder that should *NOT* be published as part of the custom node delivered to end users.
- Users: Developers who wish to publish custom nodes in the Comfy Node Registry
- Goals: Enable feature where files required or useful for development or developers, are not published to end-users.
***************
## Rationale:
The example below is from files and directories in my project that should not be installed in the `custom_nodes` folder of ComfyUI for end users or server operators:
- The `.git` files and directories should not be copied to end-users for several reasons. First, they are large, and are a waste of space for non-developers. Second, the repository history contains files that are only appropriate for developers who have agreed to development terms-of-use.
- The `.idea`, and `.github` folders are local project specific, and might contain sensitive data. They should not be included in the git repository. But if they accidentally are, they should never be uploaded to the Node Registry.
- The `project.toml` file is specific to a particular github project, and is not useful outside development.
- The `README.md` is also for developers, not end users. It will confuse users who don't code in python. The `README.md`  gets its pictures from the `illustrations` directory. The `illustrations` directory also contains large raw GIMP xcf files that are exported into pngs. Furthermore, there are layers in the xcf files which can only be released to end users when attribution conditions are met.
- `demonstrator.py` is a python file used for testing and evaluating internal node code. Publishing this it makes ComfyUI log warning and error messages. It has no no use for end-users.
***************
## Scenario:
The exclude: key is at an appropriate level in the `publish.yml`, probably at the top level. The data-type of the value is an array of strings. Each string is a case-sensitive regular expression, that can match the name of a file or directory at the root of the project.

## Example:
```
exclude:
- "\.git"
- "\.github"
- "\.idea"
- "\.gitignore"
- "demonstrator.py"
- "illustrations"
- "project.toml"
- "README.md"
```
