Installation
============

vcs2l can be installed through multiple package managers.
Choose the method that best fits your environment.

Pip
---
Vcs2l is available through `pip <https://pypi.org/project/vcs2l/>`_.
You can install it using the following command:

.. code-block:: bash

    pip3 install vcs2l

Ubuntu/Debian
-------------
Install the Debian package by adding the ``ros2-apt-source`` repository to your system.
Follow the official guide for your selected ROS Distro namely
`Rolling <https://docs.ros.org/en/rolling/Installation/Ubuntu-Install-Debs.html#enable-required-repositories>`_,
`Kilted <https://docs.ros.org/en/kilted/Installation/Ubuntu-Install-Debs.html#enable-required-repositories>`_,
`Jazzy <https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html#enable-required-repositories>`_ or
`Humble <https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html#setup-sources>`_ for this addition.
This is a **required** step for installing vcs2l on Debian-based systems.

Then, install vcs2l:

.. code-block:: bash

   sudo apt-get install python3-vcs2l

Conda
-----
If you prefer using conda, you can install vcs2l from the `conda-forge <https://anaconda.org/conda-forge/vcs2l>`_ channel:

.. code-block:: bash

   conda install -c conda-forge vcs2l

Verifying the Installation
---------------------------
After installation, you can verify that vcs2l is installed correctly by running:

.. code-block:: bash

   $ vcs
    usage: vcs <command>

    Most commands take directory arguments, recursively searching for repositories
    in these directories.  If no arguments are supplied to a command, it recurses
    on the current directory (inclusive) by default.

    The available commands are:
    branch     Show the branches
    custom     Run a custom command
    delete     Remove the directories indicated by the list of given repositories.
    diff       Show changes in the working tree
    export     Export the list of repositories
    import     Import the list of repositories
    log        Show commit logs
    pull       Bring changes from the repository into the working copy
    push       Push changes from the working copy to the repository
    remotes    Show the URL of the repository
    status     Show the working tree status
    validate   Validate the repository list file

    See 'vcs <command> --help' for more information on a specific command.
