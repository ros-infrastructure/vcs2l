^^^^^^^^^^^^^^^^^^^^^^^^^^^
Changelog for package vcs2l
^^^^^^^^^^^^^^^^^^^^^^^^^^^
1.1.5 (2025-09-12)
------------------
* Ignore nondeterministic line ordering in test_commands (`#66 <https://github.com/ros-infrastructure/vcs2l/pull/66>`_)
* Reduce unnecessary console output validation in test_commands (`#67 <https://github.com/ros-infrastructure/vcs2l/pull/67>`_)
* Added sphinx auto documentation (`#52 <https://github.com/ros-infrastructure/vcs2l/pull/52>`_)
* Fix CVE-2007-4559 warnings in RHEL tar extraction. (`#62 <https://github.com/ros-infrastructure/vcs2l/pull/62>`_)
* Disable Python warnings when capturing console output (`#61 <https://github.com/ros-infrastructure/vcs2l/pull/61>`_)
* Fix dependency for entry_points import (`#65 <https://github.com/ros-infrastructure/vcs2l/pull/65>`_)
* Bump minimum Python version to 3.6 (`#64 <https://github.com/ros-infrastructure/vcs2l/pull/64>`_)
* Explicitly set a static global git configuration while testing (`#58 <https://github.com/ros-infrastructure/vcs2l/pull/58>`_)
* Drop test dependencies on unused linters (`#63 <https://github.com/ros-infrastructure/vcs2l/pull/63>`_)
* Drop license classifier in favor of SPDX expression (`#60 <https://github.com/ros-infrastructure/vcs2l/pull/60>`_)
* Added DCO instructions to contributing guidelines. (`#44 <https://github.com/ros-infrastructure/vcs2l/pull/44>`_)
* 🛠️ Bump pypa/gh-action-pypi-publish from 1.12.4 to 1.13.0 (`#57 <https://github.com/ros-infrastructure/vcs2l/pull/57>`_)
* 🛠️ Bump actions/setup-python from 5.6.0 to 6.0.0 (`#56 <https://github.com/ros-infrastructure/vcs2l/pull/56>`_)

Contributors: Leander Stephen D'Souza, Scott K Logan

1.1.4 (2025-08-28)
------------------
* Migrated README from reStructuredText to Markdown. (`#51 <https://github.com/ros-infrastructure/vcs2l/pull/51>`_)
* Added option to delete repositories listed in a YAML file. (`#40 <https://github.com/ros-infrastructure/vcs2l/pull/40>`_)
* Added manual release workflow with .whl and .tar.gz artifacts. (`#36 <https://github.com/ros-infrastructure/vcs2l/pull/36>`_)
* Updated issue templates to have top-level keys. (`#50 <https://github.com/ros-infrastructure/vcs2l/pull/50>`_)
* Added CODE_OF_CONDUCT.md and SECURITY.md files to improve repository visibility and governance. (`#24 <https://github.com/ros-infrastructure/vcs2l/pull/24>`_)
* Enable test run on mercurial and subversion (`#42 <https://github.com/ros-infrastructure/vcs2l/pull/42>`_)
* Add python 3.7 and 3.8 to CI workflow. (`#37 <https://github.com/ros-infrastructure/vcs2l/pull/37>`_)
* Added yamlint and --lint option to vcs import (`#33 <https://github.com/ros-infrastructure/vcs2l/pull/33>`_)
* Contributors: Leander Stephen D'Souza

1.1.3 (2025-08-20)
------------------
* Fix: UnboundLocalError: local variable 'version_type' referenced before assignment (`#15 <https://github.com/ros-infrastructure/vcs2l/pull/15>`_)
* Enabled command retry on vcs import. (`#34 <https://github.com/ros-infrastructure/vcs2l/pull/34>`_)
* Added support for empty repository entries and improved validation output. (`#35 <https://github.com/ros-infrastructure/vcs2l/pull/35>`_)
* Add ruff to the pre-commit (`#27 <https://github.com/ros-infrastructure/vcs2l/pull/27>`_)
* 🛠️ Bump actions/checkout from 4.2.2 to 5.0.0 (`#31 <https://github.com/ros-infrastructure/vcs2l/pull/31>`_)
* 🛠️ Bump actions/setup-python from 5.5.0 to 5.6.0 (`#32 <https://github.com/ros-infrastructure/vcs2l/pull/32>`_)
* Add contribution templates (`#23 <https://github.com/ros-infrastructure/vcs2l/pull/23>`_)
* Restrict push workflow to main branch. (`#30 <https://github.com/ros-infrastructure/vcs2l/pull/30>`_)
* Add GitHub actions to the dependabot configuration. (`#28 <https://github.com/ros-infrastructure/vcs2l/pull/28>`_)
* Rename master branch reference to main in tests. (`#29 <https://github.com/ros-infrastructure/vcs2l/pull/29>`_)
* Contributors: Leander Stephen D'Souza, Stefan Hoffmann, Yuki Furuta.

1.1.2 (2025-08-02)
------------------
* Configuration updates for stdeb release to bootstrap repository. (`#25 <https://github.com/ros-infrastructure/vcs2l/pull/25>`_)

1.1.1 (2025-07-30)
------------------
* Changed base python version to 3.5. (`#21 <https://github.com/ros-infrastructure/vcs2l/pull/21>`_)
* Release 1.1.1 (`#22 <https://github.com/ros-infrastructure/vcs2l/pull/22>`_)

1.1.0 (2025-07-11)
------------------
* Fix GitHub workflow to pass on Ubuntu/Mac/Windows (`#2 <https://github.com/ros-infrastructure/vcs2l/pull/2>`_)
* Deprecate pkg_resources in favor of importlib.metadata (`#4 <https://github.com/ros-infrastructure/vcs2l/pull/4>`_)
* Updated documentation to point to the new vcs2l name. (`#12 <https://github.com/ros-infrastructure/vcs2l/pull/12>`_)
* Added ignores for pytest cache, bytecode, and virtual environments. (`#10 <https://github.com/ros-infrastructure/vcs2l/pull/10>`_)
* Added base pre-commit hooks for whitespaces and trailing newlines. (`#6 <https://github.com/ros-infrastructure/vcs2l/pull/6>`_)
* Add codespell as a pre-commit hook (`#11 <https://github.com/ros-infrastructure/vcs2l/pull/11>`_)
* Migrate python package to vcs2l (`#16 <https://github.com/ros-infrastructure/vcs2l/pull/16>`_)
* Add Python 3.5 support (`#19 <https://github.com/ros-infrastructure/vcs2l/pull/19>`_)
* Migrate tests to use ros-infrastructure links (`#17 <https://github.com/ros-infrastructure/vcs2l/pull/17>`_)
* Prep for release (`#13 <https://github.com/ros-infrastructure/vcs2l/pull/13>`_)
* Contributors: Leander Stephen D'Souza
