"""Setup script for the vcs2l package."""

import os

from setuptools import find_packages, setup

from vcs2l import __version__

with open(
    os.path.join(os.path.dirname(__file__), 'README.md'), 'r', encoding='utf-8'
) as f:
    long_description = f.read()

setup(
    name='vcs2l',
    version=__version__,
    requires_python='>=3.5',
    install_requires=['PyYAML', 'setuptools'],
    extras_require={
        'test': [
            'pytest',
        ]
    },
    packages=find_packages(),
    author='Dirk Thomas',
    author_email='web@dirk-thomas.net',
    maintainer='ROS Infrastructure Team',
    project_urls={
        'Source code': 'https://github.com/ros-infrastructure/vcs2l',
        'Issue tracker': 'https://github.com/ros-infrastructure/vcs2l/issues',
    },
    url='https://github.com/ros-infrastructure/vcs2l',
    keywords=['vcs', 'version control', 'git', 'hg', 'svn', 'bzr'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Software Development :: Version Control',
        'Topic :: Utilities',
    ],
    description='vcs2l provides a command line tool to invoke vcs commands '
    'on multiple repositories.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='Apache-2.0',
    data_files=[
        (
            'share/vcs2l-completion',
            [
                'vcs2l-completion/vcs.bash',
                'vcs2l-completion/vcs.tcsh',
                'vcs2l-completion/vcs.zsh',
                'vcs2l-completion/vcs.fish',
            ],
        )
    ],
    entry_points={
        'console_scripts': [
            'vcs = vcs2l.commands.vcs:main',
            'vcs-branch = vcs2l.commands.branch:main',
            'vcs-bzr = vcs2l.commands.custom:bzr_main',
            'vcs-custom = vcs2l.commands.custom:main',
            'vcs-delete = vcs2l.commands.delete:main',
            'vcs-diff = vcs2l.commands.diff:main',
            'vcs-export = vcs2l.commands.export:main',
            'vcs-git = vcs2l.commands.custom:git_main',
            'vcs-help = vcs2l.commands.help:main',
            'vcs-hg = vcs2l.commands.custom:hg_main',
            'vcs-import = vcs2l.commands.import_:main',
            'vcs-log = vcs2l.commands.log:main',
            'vcs-pull = vcs2l.commands.pull:main',
            'vcs-push = vcs2l.commands.push:main',
            'vcs-remotes = vcs2l.commands.remotes:main',
            'vcs-status = vcs2l.commands.status:main',
            'vcs-svn = vcs2l.commands.custom:svn_main',
            'vcs-validate = vcs2l.commands.validate:main',
        ]
    },
)
