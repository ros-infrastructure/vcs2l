Installation
============

vcs2l can be installed through multiple package managers.
Choose the method that best fits your environment.

pip
---
The recommended way to install vcs2l is through `pip <https://pypi.org/project/vcs2l/>`_.
You can install it using the following command:

.. code-block:: bash

    pip3 install vcs2l

conda
-----
If you prefer using conda, you can install vcs2l from the `conda-forge <https://anaconda.org/conda-forge/vcs2l>`_ channel:

.. code-block:: bash

   conda install -c conda-forge vcs2l

debian
------
Install the debian package by adding the ``ros2-apt-source`` repository to your system by following the
`ROS 2 <https://docs.ros.org/en/kilted/Installation/Ubuntu-Install-Debs.html>`_
installation instructions for your distribution.

Then, install vcs2l:

.. code-block:: bash

   sudo apt-get install python3-vcs2l

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
