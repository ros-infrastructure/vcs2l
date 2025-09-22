# What is vcs2l?

Vcs2l is a fork of Dirk Thomas's [`vcstool`](https://github.com/dirk-thomas/vcstool/) which is a version control system (VCS) tool, designed to make working with multiple repositories easier.

This fork is created to continue the development of `vcstool`, as it is no longer actively maintained.

The commands provided by vcs2l have the same naming structure as the original fork, so it can be used as a drop-in replacement. Therefore, the repository is renamed to `vcs2l` while maintaining the command names to `vcstool` to ensure compatibility with existing scripts and workflows.

For more information on how to use vcs2l, please refer to the [**documentation**](https://ros-infrastructure.github.io/vcs2l/index.html).

### Note:
This tool should not be confused with [vcstools](https://github.com/vcstools/vcstools/) (with a trailing `s`) which provides a Python API for interacting with different version control systems.

The biggest differences between the two are:
- `vcstool` doesn't use any state beside the repository working copies available in the filesystem.
- The file format of `vcstool export` uses the relative paths of the repositories as keys in YAML which avoids collisions by design.
- `vcstool` has significantly fewer lines of code than `vcstools` including the command line tools built on top.

## Python 3.6+ support

The latest version supports Python 3.6 and newer.
However, the CI is only run on Python 3.7 and newer, as there are no suitable GitHub Actions [runners](https://raw.githubusercontent.com/actions/python-versions/main/versions-manifest.json/) available for Python 3.6.
Additionally, Debian packages can only be built for platforms with Python 3.8 and newer.

## How does it work?

Vcs2l operates on any folder from where it recursively searches for supported repositories. On these repositories vcs2l invokes the native VCS client with the requested command (i.e. *diff*).

## Which VCS types are supported?

Vcs2l supports [Git](http://git-scm.com), [Mercurial](https://www.mercurial-scm.org/), [Subversion](http://subversion.apache.org), [Bazaar](http://bazaar.canonical.com/en/).

## How to use vcs2l?

The script `vcs` can be used similarly to the VCS clients `git`, `hg` etc. The `help` command provides a list of available commands with an additional description:

```bash
vcs help
```

By default, vcs2l searches for repositories under the current folder. Optionally one path (or multiple paths) can be passed to search for repositories at different locations:

```bash
vcs status /path/to/several/repos /path/to/other/repos /path/to/single/repo
```

## Exporting and importing sets of repositories

Vcs2l can export and import all the information required to reproduce the versions of a set of repositories. Vcs2l uses a simple [YAML](http://www.yaml.org/) format to encode this information.

This format includes a root key `repositories` under which each local repository is described by a dictionary keyed by its relative path. Each of these dictionaries contains keys `type`, `url`, and `version`. If the `version` key is omitted the default branch is being used.

This results in something similar to the following for a set of two repositories ([vcs2l](https://github.com/ros-infrastructure/vcs2l) cloned via Git and [rosinstall](http://github.com/vcstools/rosinstall) checked out via Subversion):

```yaml
repositories:
  vcs2l:
    type: git
    url: git@github.com:ros-infrastructure/vcs2l.git
    version: main
  old_tools/rosinstall:
    type: svn
    url: https://github.com/vcstools/rosinstall/trunk
    version: 748
```

### Export set of repositories

The `vcs export` command outputs the path, vcs type, URL and version information for all repositories in [YAML](http://www.yaml.org/) format. The output is usually piped to a file:

```bash
vcs export > my.repos
```

If the repository is currently on the tip of a branch the branch is followed. This implies that a later import might fetch a newer revision if the branch has evolved in the meantime. Furthermore if the local branch has evolved from the remote repository an import might not result in the exact same state.

To make sure to store the exact revision in the exported data use the command line argument `--exact`. Since a specific revision is not tied to neither a branch nor a remote (for Git and Mercurial) the tool will check if the current hash exists in any of the remotes. If it exists in multiple the remotes `origin` and `upstream` are considered before any other in alphabetical order.

For compatibility with [yamllint](https://yamllint.readthedocs.io/en/stable/) the output can be formatted by passing the command line argument `--lint`. This would add the document start and end markers (`---` and `...`) to the output.

### Import set of repositories

The `vcs import` command clones all repositories which are passed in via `stdin` in YAML format. Usually the data of a previously exported file is piped in:

```bash
vcs import < my.repos
```

The `import` command also supports input in the [rosinstall file format](http://www.ros.org/doc/independent/api/rosinstall/html/rosinstall_file_format.html). Beside passing a file path the command also supports passing a URL.

Only for this command vcs2l supports the pseudo clients `tar` and `zip` which fetch a tarball / zipfile from a URL and unpack its content. For those two types the `version` key is optional. If specified only entries from the archive which are in the subfolder specified by the version value are being extracted.

### Import with extends functionality

The `vcs import` command supports an `extends` key at the top level of the YAML file. The value of that key is a path or URL to another YAML file which is imported first.
This base file can itself also contain the key to chain multiple files. The extension to this base file is given precedence over the parent in case of duplicate repository entries.

#### Normal Extension

For instance, consider the following two files:

- **`base.repos`**: contains three repositories `vcs2l`, `immutable/hash` and `immutable/tag`, checked out at specific versions.

   ```yaml
   ---
   repositories:
     vcs2l:
       type: git
       url: https://github.com/ros-infrastructure/vcs2l.git
       version: main
     immutable/hash:
       type: git
       url: https://github.com/ros-infrastructure/vcs2l.git
       version: 377d5b3d03c212f015cc832fdb368f4534d0d583
     immutable/tag:
       type: git
       url: https://github.com/ros-infrastructure/vcs2l.git
       version: 1.1.3
   ```

- **`base_extension.repos`**: extends the base file and overrides the version of `immutable/hash` and `immutable/tag` repositories.

   ```yaml
   ---
   extends: base.repos
   repositories:
     immutable/hash:
       type: git
       url: https://github.com/ros-infrastructure/vcs2l.git
       version: 25e4ae2f1dd28b0efcd656f4b1c9679d8a7d6c22
     immutable/tag:
       type: git
       url: https://github.com/ros-infrastructure/vcs2l.git
       version: 1.1.5
   ```
The resulting extension import would import vcs2l at version `main`, `immutable/hash` at version `25e4ae2` and `immutable/tag` at version `1.1.5`.

#### Multiple Extensions

The `extends` key also supports a list of files to extend from. The files are imported in the order they are specified and the precedence is given to the last file in case of duplicate repository entries.

For instance, consider the following three files:

- **`base_1.repos`**: contains two repositories `vcs2l` and `immutable/hash`, checked out at `1.1.3`.

   ```yaml
   ---
   repositories:
    immutable/hash:
      type: git
      url: https://github.com/ros-infrastructure/vcs2l.git
      version: e700793cb2b8d25ce83a611561bd167293fd66eb  # 1.1.3
     vcs2l:
       type: git
       url: https://github.com/ros-infrastructure/vcs2l.git
       version: 1.1.3
    ```

- **`base_2.repos`**: contains two repositories `vcs2l` and `immutable/hash`, checked out at `1.1.4`.

   ```yaml
   ---
   repositories:
    immutable/hash:
      type: git
      url: https://github.com/ros-infrastructure/vcs2l.git
      version: 2c7ff89d12d8a77c36b60d1f7ba3039cdd3f742b  # 1.1.4
     vcs2l:
       type: git
       url: https://github.com/ros-infrastructure/vcs2l.git
       version: 1.1.4
  ```

- **`multiple_extension.repos`**: extends both base files and overrides the version of `vcs2l` repository.

   ```yaml
   ---
   extends:
     - base_1.repos  # Lower priority
     - base_2.repos  # Higher priority
   repositories:
     vcs2l:
       type: git
       url: https://github.com/ros-infrastructure/vcs2l.git
       version: 1.1.5
   ```

The resulting extension import would import `immutable/hash` at version `1.1.4` (from `base_2.repos`) and `vcs2l` at version `1.1.5`.

Duplicate file names in the `extends` list are not allowed and would raise the following error:

```bash
Duplicate entries found in extends in file: <relative-path>/multiple_extension.repos
```

#### Circular Loop Protection

In order to avoid infinite loops in case of circular imports the tool detects already imported files and raises an error if such a file is encountered again.

For instance, consider the following two files:

- **`loop_base.repos`**: extends the `loop_extension.repos` file, and contains two repositories `vcs2l` and `immutable/tag`.

   ```yaml
   ---
   extends: loop_extension.repos
   repositories:
     vcs2l:
       type: git
       url: https://github.com/ros-infrastructure/vcs2l.git
       version: main
     immutable/tag:
       type: git
       url: https://github.com/ros-infrastructure/vcs2l.git
       version: 1.1.3
   ```

- **`loop_extension.repos`**: extends the `loop_base.repos` file, and modifies the version of `immutable/tag` with `1.1.5`.

   ```yaml
   ---
   extends: loop_base.repos
   repositories:
     immutable/tag:
       type: git
       url: https://github.com/ros-infrastructure/vcs2l.git
       version: 1.1.5
   ```
The resulting extension import would prevent the download and raise the following error:

```bash
Circular import detected: <relative-path>/loop_extension.repos
```

#### File path behaviour

Currently there are two ways to specify the path to the repository file passed to `vcs import`:

1. **Recommended**: Using `--input`.

   * For instance: `vcs import --input my.repos <destination-path>`

   * The extended files are searched relative to the file containing the `extends` key.

   * You do not require to be in the same directory as `my.repos` to run the command.

2. Using the input redirection operator `<` to pass a local file path via `stdin`.

   * For instance: `vcs import < my.repos <destination-path>`

    * The extended files are searched relative to the current working directory.

    * Therefore, you have to be in the **same** directory as `my.repos` to run the command. In addition, all the extended files must also be relative to the current working directory.

### Delete set of repositories

The `vcs delete` command removes all directories of repositories which are passed in via `stdin` in YAML format.

By default, the command performs a dry-run and only lists the directories which would be deleted.
In addition, it would convey warnings for missing directories and skip invalid paths upon which no action is taken.

To  delete the directories the `-f/--force` argument must be passed:

```bash
$ vcs delete < test/list.repos

Warning: The following paths do not exist:
  ./immutable/hash
  ./immutable/hash_tar
  ./immutable/hash_zip
  ./immutable/tag
  ./without_version
The following paths will be deleted:
  ./vcs2l
Dry-run mode: No directories were deleted. Use -f/--force to delete them.
```

### Validate repositories file

The `vcs validate` command takes a YAML file which is passed in via `stdin` and validates its contents and format. The data of a previously-exported file or hand-generated file are piped in:

```bash
vcs validate < my.repos
```

The `validate` command also supports input in the [rosinstall file format](http://www.ros.org/doc/independent/api/rosinstall/html/rosinstall_file_format.html).

## Advanced features

### Show log since last tag

The `vcs log` command supports the argument `--limit-untagged` which will output the log for all commits since the last tag.

### Parallelization and stdin

By default `vcs` parallelizes the work across multiple repositories based on the number of CPU cores. In the case that the invoked commands require input from `stdin` that parallelization is a problem. In order to be able to provide input to each command separately these commands must run sequentially.

When needing to e.g. interactively provide credentials all commands should be executed sequentially by passing:

```bash
--workers 1
```

In the case repositories are using SSH `git@` URLs but the host is not known yet `vcs import` automatically falls back to a single worker.

### Run arbitrary commands

The `vcs custom` command enables to pass arbitrary user-specified arguments to the vcs invocation. The set of repositories to operate on can optionally be restricted by the type:

```bash
vcs custom --git --args log --oneline -n 10
```

If the command should work on multiple repositories make sure to pass only generic arguments which work for all of these repository types.

# How to install vcs2l?

On Debian-based platforms the recommended method is to install the package *python3-vcs2l*. On Ubuntu this is done using *apt-get*:

If you are using [ROS](https://www.ros.org/) you can get the package directly from the ROS repository:

```bash
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
sudo apt install curl # if you haven't already installed curl
curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get install python3-vcs2l
```

On other systems, use the [PyPI](https://pypi.org/project/vcs2l/) package:

```bash
pip3 install vcs2l
```

## Setup auto-completion

For the shells *bash*, *tcsh* and *zsh* vcs2l can provide auto-completion of the various VCS commands. In order to enable that feature the shell specific completion file must be sourced.

For *bash* append the following line to the `~/.bashrc` file:

```bash
source /usr/share/vcs2l-completion/vcs.bash
```

For *tcsh* append the following line to the `~/.cshrc` file:

```tcsh
source /usr/share/vcs2l-completion/vcs.tcsh
```

For *zsh* append the following line to the `~/.zshrc` file:

```zsh
source /usr/share/vcs2l-completion/vcs.zsh
```

For *fish* append the following line to the `~/.config/fishconfig.fish` file:

```fish
source /usr/share/vcs2l-completion/vcs.fish
```

# How to contribute?

## How to report problems?

Before reporting a problem please make sure to use the latest version. Issues can be filled on [GitHub](https://github.com/ros-infrastructure/vcs2l/issues) after making sure that this problem has not yet been reported.

Please make sure to include as much information, i.e. version numbers from vcs2l, operating system, Python and a reproducible example of the commands which expose the problem.

## How to try the latest changes?

Sourcing the `setup.sh` file prepends the `src` folder to the `PYTHONPATH` and the `scripts` folder to the `PATH`. Then vcs2l can be used with the commands `vcs-COMMAND` (note the hyphen between `vcs` and `command` instead of a space).

Alternatively the `-e/--editable` flag of `pip` can be used:

```bash
# from the top level of this repo
pip3 install --user -e .
```

## How to build the documentation?

The documentation is built using [Sphinx](http://sphinx-doc.org/) and can be built locally after installing the package by running:

```bash
cd docs
make html
```
The generated HTML files can be found in `docs/build/html/index.html` and opened in a web browser.
