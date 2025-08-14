# resp

./install_mg.sh

```bash
[MG_User@localhost ~/tmp %] mkdir moduli_generator && cd moduli_generator  [15:57:00]
[MG_User@localhost ~/tmp/moduli_generator %] curl -fsSL -o install_mg.sh \ [15:57:35]
  https://raw.githubusercontent.com/beckerwilliams/moduli_generator/HEAD/data/bash_scripts/install_mg.sh
[MG_User@localhost ~/tmp/moduli_generator %] chmod +x install_mg.sh        [15:57:48]
[MG_User@localhost ~/tmp/moduli_generator %] ./install_mg.sh               [15:57:58]
Project Name: moduli_generator
	WORK_DIR: .moduli_generator_build_env
	CWD: /Users/MG_User/tmp/moduli_generator
[ Verifying System Requirements ]
✓ Git is installed: git version 2.39.5 (Apple Git-154)
✓ Python 3.12 is installed (≥3.12 required): Python 3.12.11
✓ All requirements verified successfully
[ Database Configuration ]
Enter MariaDB host [localhost]: 
Enter MariaDB port [3306]: 
Enter database name [moduli_db]: 
Enter MariaDB username [moduli_generator]: 
Enter MariaDB password: 
✓ Database configuration complete
*** Project Name: moduli_generator
	WORK_DIR: .moduli_generator_build_env
	CWD: /Users/MG_User/tmp/moduli_generator ***
[ Saving Current Directory /Users/MG_User/tmp/moduli_generator, entering .moduli_generator_build_env ]
[ Cloning moduli_generator from Github ]
Cloning into 'moduli_generator'...
remote: Enumerating objects: 1738, done.
remote: Counting objects: 100% (1144/1144), done.
remote: Compressing objects: 100% (653/653), done.
remote: Total 1738 (delta 687), reused 877 (delta 454), pack-reused 594 (from 1
Receiving objects: 100% (1738/1738), 35.70 MiB | 72.40 MiB/s, done.
Resolving deltas: 100% (991/991), done.
[ Entering Moduli Dev Directory ]
✓ Poetry/PEP 621 project configuration found
[ Creating and Activating Moduli Generator's Wheel Builder ]
✓ Virtual environment activated
Using pip: /Users/MG_User/tmp/moduli_generator/.moduli_generator_build_env/moduli_generator/.venv/bin/pip
[ Upgrading pip ]
Requirement already satisfied: pip in ./.venv/lib/python3.12/site-packages (25.1.1)
Collecting pip
  Using cached pip-25.2-py3-none-any.whl.metadata (4.7 kB)
Using cached pip-25.2-py3-none-any.whl (1.8 MB)
Installing collected packages: pip
  Attempting uninstall: pip
    Found existing installation: pip 25.1.1
    Uninstalling pip-25.1.1:
      Successfully uninstalled pip-25.1.1
Successfully installed pip-25.2
[ Installing Poetry in virtual environment ]
Collecting poetry==1.8.3
  Using cached poetry-1.8.3-py3-none-any.whl.metadata (6.8 kB)
Collecting build<2.0.0,>=1.0.3 (from poetry==1.8.3)
  Using cached build-1.3.0-py3-none-any.whl.metadata (5.6 kB)
Collecting cachecontrol<0.15.0,>=0.14.0 (from cachecontrol[filecache]<0.15.0,>=0.14.0->poetry==1.8.3)
  Using cached cachecontrol-0.14.3-py3-none-any.whl.metadata (3.1 kB)
Collecting cleo<3.0.0,>=2.1.0 (from poetry==1.8.3)
  Using cached cleo-2.1.0-py3-none-any.whl.metadata (12 kB)
Collecting crashtest<0.5.0,>=0.4.1 (from poetry==1.8.3)
  Using cached crashtest-0.4.1-py3-none-any.whl.metadata (1.1 kB)
Collecting dulwich<0.22.0,>=0.21.2 (from poetry==1.8.3)
  Using cached dulwich-0.21.7-cp312-cp312-macosx_10_9_x86_64.whl.metadata (4.3 kB)
Collecting fastjsonschema<3.0.0,>=2.18.0 (from poetry==1.8.3)
  Using cached fastjsonschema-2.21.1-py3-none-any.whl.metadata (2.2 kB)
Collecting installer<0.8.0,>=0.7.0 (from poetry==1.8.3)
  Using cached installer-0.7.0-py3-none-any.whl.metadata (936 bytes)
Collecting keyring<25.0.0,>=24.0.0 (from poetry==1.8.3)
  Using cached keyring-24.3.1-py3-none-any.whl.metadata (20 kB)
Collecting packaging>=23.1 (from poetry==1.8.3)
  Using cached packaging-25.0-py3-none-any.whl.metadata (3.3 kB)
Collecting pexpect<5.0.0,>=4.7.0 (from poetry==1.8.3)
  Using cached pexpect-4.9.0-py2.py3-none-any.whl.metadata (2.5 kB)
Collecting pkginfo<2.0,>=1.10 (from poetry==1.8.3)
  Using cached pkginfo-1.12.1.2-py3-none-any.whl.metadata (13 kB)
Collecting platformdirs<5,>=3.0.0 (from poetry==1.8.3)
  Using cached platformdirs-4.3.8-py3-none-any.whl.metadata (12 kB)
Collecting poetry-core==1.9.0 (from poetry==1.8.3)
  Using cached poetry_core-1.9.0-py3-none-any.whl.metadata (3.5 kB)
Collecting poetry-plugin-export<2.0.0,>=1.6.0 (from poetry==1.8.3)
  Using cached poetry_plugin_export-1.9.0-py3-none-any.whl.metadata (3.1 kB)
Collecting pyproject-hooks<2.0.0,>=1.0.0 (from poetry==1.8.3)
  Using cached pyproject_hooks-1.2.0-py3-none-any.whl.metadata (1.3 kB)
Collecting requests<3.0,>=2.26 (from poetry==1.8.3)
  Using cached requests-2.32.4-py3-none-any.whl.metadata (4.9 kB)
Collecting requests-toolbelt<2.0.0,>=1.0.0 (from poetry==1.8.3)
  Using cached requests_toolbelt-1.0.0-py2.py3-none-any.whl.metadata (14 kB)
Collecting shellingham<2.0,>=1.5 (from poetry==1.8.3)
  Using cached shellingham-1.5.4-py2.py3-none-any.whl.metadata (3.5 kB)
Collecting tomlkit<1.0.0,>=0.11.4 (from poetry==1.8.3)
  Using cached tomlkit-0.13.3-py3-none-any.whl.metadata (2.8 kB)
Collecting trove-classifiers>=2022.5.19 (from poetry==1.8.3)
  Using cached trove_classifiers-2025.8.6.13-py3-none-any.whl.metadata (2.3 kB)
Collecting virtualenv<21.0.0,>=20.23.0 (from poetry==1.8.3)
  Using cached virtualenv-20.33.1-py3-none-any.whl.metadata (4.5 kB)
Collecting xattr<2.0.0,>=1.0.0 (from poetry==1.8.3)
  Using cached xattr-1.2.0-cp312-cp312-macosx_10_13_x86_64.whl.metadata (3.8 kB)
Collecting msgpack<2.0.0,>=0.5.2 (from cachecontrol<0.15.0,>=0.14.0->cachecontrol[filecache]<0.15.0,>=0.14.0->poetry==1.8.3)
  Using cached msgpack-1.1.1-cp312-cp312-macosx_10_13_x86_64.whl.metadata (8.4 kB)
Collecting filelock>=3.8.0 (from cachecontrol[filecache]<0.15.0,>=0.14.0->poetry==1.8.3)
  Using cached filelock-3.18.0-py3-none-any.whl.metadata (2.9 kB)
Collecting rapidfuzz<4.0.0,>=3.0.0 (from cleo<3.0.0,>=2.1.0->poetry==1.8.3)
  Using cached rapidfuzz-3.13.0-cp312-cp312-macosx_10_13_x86_64.whl.metadata (12 kB)
Collecting urllib3>=1.25 (from dulwich<0.22.0,>=0.21.2->poetry==1.8.3)
  Using cached urllib3-2.5.0-py3-none-any.whl.metadata (6.5 kB)
Collecting jaraco.classes (from keyring<25.0.0,>=24.0.0->poetry==1.8.3)
  Using cached jaraco.classes-3.4.0-py3-none-any.whl.metadata (2.6 kB)
Collecting ptyprocess>=0.5 (from pexpect<5.0.0,>=4.7.0->poetry==1.8.3)
  Using cached ptyprocess-0.7.0-py2.py3-none-any.whl.metadata (1.3 kB)
INFO: pip is looking at multiple versions of poetry-plugin-export to determine which version is compatible with other requirements. This could take a while.
Collecting poetry-plugin-export<2.0.0,>=1.6.0 (from poetry==1.8.3)
  Using cached poetry_plugin_export-1.8.0-py3-none-any.whl.metadata (2.8 kB)
Collecting charset_normalizer<4,>=2 (from requests<3.0,>=2.26->poetry==1.8.3)
  Using cached charset_normalizer-3.4.3-cp312-cp312-macosx_10_13_universal2.whl.metadata (36 kB)
Collecting idna<4,>=2.5 (from requests<3.0,>=2.26->poetry==1.8.3)
  Using cached idna-3.10-py3-none-any.whl.metadata (10 kB)
Collecting certifi>=2017.4.17 (from requests<3.0,>=2.26->poetry==1.8.3)
  Using cached certifi-2025.8.3-py3-none-any.whl.metadata (2.4 kB)
Collecting distlib<1,>=0.3.7 (from virtualenv<21.0.0,>=20.23.0->poetry==1.8.3)
  Using cached distlib-0.4.0-py2.py3-none-any.whl.metadata (5.2 kB)
Collecting cffi>=1.16.0 (from xattr<2.0.0,>=1.0.0->poetry==1.8.3)
  Using cached cffi-1.17.1-cp312-cp312-macosx_10_9_x86_64.whl.metadata (1.5 kB)
Collecting pycparser (from cffi>=1.16.0->xattr<2.0.0,>=1.0.0->poetry==1.8.3)
  Using cached pycparser-2.22-py3-none-any.whl.metadata (943 bytes)
Collecting more-itertools (from jaraco.classes->keyring<25.0.0,>=24.0.0->poetry==1.8.3)
  Using cached more_itertools-10.7.0-py3-none-any.whl.metadata (37 kB)
Using cached poetry-1.8.3-py3-none-any.whl (249 kB)
Using cached poetry_core-1.9.0-py3-none-any.whl (309 kB)
Using cached build-1.3.0-py3-none-any.whl (23 kB)
Using cached cachecontrol-0.14.3-py3-none-any.whl (21 kB)
Using cached cleo-2.1.0-py3-none-any.whl (78 kB)
Using cached crashtest-0.4.1-py3-none-any.whl (7.6 kB)
Using cached dulwich-0.21.7-cp312-cp312-macosx_10_9_x86_64.whl (475 kB)
Using cached fastjsonschema-2.21.1-py3-none-any.whl (23 kB)
Using cached installer-0.7.0-py3-none-any.whl (453 kB)
Using cached keyring-24.3.1-py3-none-any.whl (38 kB)
Using cached msgpack-1.1.1-cp312-cp312-macosx_10_13_x86_64.whl (82 kB)
Using cached pexpect-4.9.0-py2.py3-none-any.whl (63 kB)
Using cached pkginfo-1.12.1.2-py3-none-any.whl (32 kB)
Using cached platformdirs-4.3.8-py3-none-any.whl (18 kB)
Using cached poetry_plugin_export-1.8.0-py3-none-any.whl (10 kB)
Using cached pyproject_hooks-1.2.0-py3-none-any.whl (10 kB)
Using cached rapidfuzz-3.13.0-cp312-cp312-macosx_10_13_x86_64.whl (2.0 MB)
Using cached requests-2.32.4-py3-none-any.whl (64 kB)
Using cached charset_normalizer-3.4.3-cp312-cp312-macosx_10_13_universal2.whl (205 kB)
Using cached idna-3.10-py3-none-any.whl (70 kB)
Using cached requests_toolbelt-1.0.0-py2.py3-none-any.whl (54 kB)
Using cached shellingham-1.5.4-py2.py3-none-any.whl (9.8 kB)
Using cached tomlkit-0.13.3-py3-none-any.whl (38 kB)
Using cached urllib3-2.5.0-py3-none-any.whl (129 kB)
Using cached virtualenv-20.33.1-py3-none-any.whl (6.1 MB)
Using cached distlib-0.4.0-py2.py3-none-any.whl (469 kB)
Using cached filelock-3.18.0-py3-none-any.whl (16 kB)
Using cached xattr-1.2.0-cp312-cp312-macosx_10_13_x86_64.whl (19 kB)
Using cached certifi-2025.8.3-py3-none-any.whl (161 kB)
Using cached cffi-1.17.1-cp312-cp312-macosx_10_9_x86_64.whl (183 kB)
Using cached packaging-25.0-py3-none-any.whl (66 kB)
Using cached ptyprocess-0.7.0-py2.py3-none-any.whl (13 kB)
Using cached trove_classifiers-2025.8.6.13-py3-none-any.whl (14 kB)
Using cached jaraco.classes-3.4.0-py3-none-any.whl (6.8 kB)
Using cached more_itertools-10.7.0-py3-none-any.whl (65 kB)
Using cached pycparser-2.22-py3-none-any.whl (117 kB)
Installing collected packages: trove-classifiers, ptyprocess, fastjsonschema, distlib, urllib3, tomlkit, shellingham, rapidfuzz, pyproject-hooks, pycparser, poetry-core, platformdirs, pkginfo, pexpect, packaging, msgpack, more-itertools, installer, idna, filelock, crashtest, charset_normalizer, certifi, virtualenv, requests, jaraco.classes, dulwich, cleo, cffi, build, xattr, requests-toolbelt, keyring, cachecontrol, poetry-plugin-export, poetry
Successfully installed build-1.3.0 cachecontrol-0.14.3 certifi-2025.8.3 cffi-1.17.1 charset_normalizer-3.4.3 cleo-2.1.0 crashtest-0.4.1 distlib-0.4.0 dulwich-0.21.7 fastjsonschema-2.21.1 filelock-3.18.0 idna-3.10 installer-0.7.0 jaraco.classes-3.4.0 keyring-24.3.1 more-itertools-10.7.0 msgpack-1.1.1 packaging-25.0 pexpect-4.9.0 pkginfo-1.12.1.2 platformdirs-4.3.8 poetry-1.8.3 poetry-core-1.9.0 poetry-plugin-export-1.8.0 ptyprocess-0.7.0 pycparser-2.22 pyproject-hooks-1.2.0 rapidfuzz-3.13.0 requests-2.32.4 requests-toolbelt-1.0.0 shellingham-1.5.4 tomlkit-0.13.3 trove-classifiers-2025.8.6.13 urllib3-2.5.0 virtualenv-20.33.1 xattr-1.2.0
Poetry (version 1.8.3)
✓ Poetry installed successfully: Poetry (version 1.8.3)
[ Installing project dependencies ]
Installing dependencies from lock file

Package operations: 42 installs, 1 update, 0 removals

  - Installing six (1.17.0)
  - Installing markupsafe (3.0.2)
  - Installing mergedeep (1.3.4)
  - Installing python-dateutil (2.9.0.post0)
  - Installing pyyaml (6.0.2)
  - Installing click (8.2.1)
  - Installing ghp-import (2.1.0)
  - Installing jinja2 (3.1.6)
  - Installing markdown (3.8.2)
  - Installing mkdocs-get-deps (0.2.0)
  - Installing pathspec (0.12.1)
  - Installing pyyaml-env-tag (1.1)
  - Installing watchdog (6.0.0)
  - Installing mkdocs (1.6.1)
  - Downgrading charset-normalizer (3.4.3 -> 3.4.2)
  - Installing colorama (0.4.6)
  - Installing iniconfig (2.1.0)
  - Installing mkdocs-autorefs (1.4.2)
  - Installing pluggy (1.6.0)
  - Installing pygments (2.19.2)
  - Installing pymdown-extensions (10.16.1)
  - Installing babel (2.17.0)
  - Installing backrefs (5.9)
  - Installing coverage (7.10.2)
  - Installing griffe (1.11.0)
  - Installing mkdocs-material-extensions (1.3.1)
  - Installing mkdocstrings (0.30.0)
  - Installing mypy-extensions (1.1.0)
  - Installing paginate (0.5.7)
  - Installing pytest (8.4.1)
  - Installing setuptools (80.9.0)
  - Installing wheel (0.45.1)
  - Installing black (25.1.0)
  - Installing configparser (7.2.0)
  - Installing mariadb (1.1.13)
  - Installing mkdocs-material (9.6.16)
  - Installing mkdocstrings-python (1.16.12)
  - Installing pip-tools (7.5.0)
  - Installing pytest-asyncio (1.1.0)
  - Installing pytest-cov (6.2.1)
  - Installing pytest-mock (3.14.1)
  - Installing toml (0.10.2)
  - Installing typing-extensions (4.14.1)

Installing the current project: moduli_generator (2.1.35)
[ Updating Poetry lock file ]
Resolving dependencies... (0.1s)
[ Building moduli_generator wheel ]
Building moduli_generator (2.1.35)
  - Building sdist
  - Built moduli_generator-2.1.35.tar.gz
  - Building wheel
  - Built moduli_generator-2.1.35-py3-none-any.whl
✓ Wheel file created: moduli_generator-2.1.35-py3-none-any.whl
[ Moduli Generator Wheel: /Users/MG_User/tmp/moduli_generator/moduli_generator-2.1.35-py3-none-any.whl ]
Deleted Temporary Work Dir: .moduli_generator_build_env
✓ Build wheel completed successfully
*** Project Name: moduli_generator
	WORK_DIR: .moduli_generator_build_env
	CWD: /Users/MG_User/tmp/moduli_generator ***
[ Creating runtime virtual environment ]
✓ Virtual environment activated
Using pip: /Users/MG_User/tmp/moduli_generator/.venv/bin/pip
[ Upgrading Virtual Environment and Installing Moduli Generator wheel ]
Requirement already satisfied: pip in ./.venv/lib/python3.12/site-packages (25.1.1)
Collecting pip
  Using cached pip-25.2-py3-none-any.whl.metadata (4.7 kB)
Using cached pip-25.2-py3-none-any.whl (1.8 MB)
Installing collected packages: pip
  Attempting uninstall: pip
    Found existing installation: pip 25.1.1
    Uninstalling pip-25.1.1:
      Successfully uninstalled pip-25.1.1
Successfully installed pip-25.2
Processing ./moduli_generator-2.1.35-py3-none-any.whl
Collecting configparser>=7.2.0 (from moduli-generator==2.1.35)
  Using cached configparser-7.2.0-py3-none-any.whl.metadata (5.5 kB)
Collecting mariadb==1.1.13 (from moduli-generator==2.1.35)
  Using cached mariadb-1.1.13-cp312-cp312-macosx_15_0_x86_64.whl
Collecting typing-extensions<5.0.0,>=4.14.1 (from moduli-generator==2.1.35)
  Using cached typing_extensions-4.14.1-py3-none-any.whl.metadata (3.0 kB)
Collecting packaging (from mariadb==1.1.13->moduli-generator==2.1.35)
  Using cached packaging-25.0-py3-none-any.whl.metadata (3.3 kB)
Using cached typing_extensions-4.14.1-py3-none-any.whl (43 kB)
Using cached configparser-7.2.0-py3-none-any.whl (17 kB)
Using cached packaging-25.0-py3-none-any.whl (66 kB)
Installing collected packages: typing-extensions, packaging, configparser, mariadb, moduli-generator
Successfully installed configparser-7.2.0 mariadb-1.1.13 moduli-generator-2.1.35 packaging-25.0 typing-extensions-4.14.1
[ Moduli Generator Installed Successfully ]
Virtual Environment Package Manifest:
Package           Version
----------------- -------
configparser      7.2.0
mariadb           1.1.13
moduli_generator  2.1.35
packaging         25.0
pip               25.2
typing_extensions 4.14.1

✓ Runtime installation completed successfully
✓ Installation completed successfully!
To activate the environment, run: source .venv/bin/activate
To test the installation, run: moduli_generator --help
```

## Verify Install: `moduli_generator --help`

```bash
[MG_User@localhost ~/tmp/moduli_generator %] moduli_generator --help       [15:58:55]
zsh: command not found: moduli_generator
[MG_User@localhost ~/tmp/moduli_generator %] venv                          [15:59:06]
((.venv) ) [MG_User@localhost ~/tmp/moduli_generator %] moduli_generator --help
usage: moduli_generator [-h] [--candidates-dir CANDIDATES_DIR]
[--key-lengths KEY_LENGTHS [KEY_LENGTHS ...]]
[--log-dir LOG_DIR] [--mariadb-cnf MARIADB_CNF]
[--moduli-dir MODULI_DIR] [--moduli-home MODULI_HOME]
[--moduli-db MODULI_DB] [--nice-value NICE_VALUE]
[--records-per-keylength RECORDS_PER_KEYLENGTH]
[--preserve-moduli-after-dbstore]
[--delete-records-on-moduli-write]

Moduli Generator - Generate and manage secure moduli for cryptographic
operations

options:
-h, --help show this help message and exit
--candidates-dir CANDIDATES_DIR
Directory to store candidate moduli (relative to
moduli-home) (default: .candidates)
--key-lengths KEY_LENGTHS [KEY_LENGTHS ...]
Space-separated list of key lengths to generate moduli
for (default: (3072, 4096, 6144, 7680, 8192))
--log-dir LOG_DIR Directory to store log files (relative to moduli_home)
(default: .logs)
--mariadb-cnf MARIADB_CNF
Path to MariaDB configuration file (relative to
moduli_home) (default: moduli_generator.cnf)
--moduli-dir MODULI_DIR
Directory to store generated moduli (relative to
moduli_home) (default: .moduli)
--moduli-home MODULI_HOME
Base directory for moduli generation and storage
(default: /Users/MG_User/.moduli_generator)
--moduli-db MODULI_DB
Name of the database to create and Initialize
(default: moduli_db)
--nice-value NICE_VALUE
Process nice value for CPU intensive operations
(default: 15)
--records-per-keylength RECORDS_PER_KEYLENGTH
Number of moduli per key-length to capture in each
produced moduli file (default: 20)
--preserve-moduli-after-dbstore
Delete records from DB written to moduli file
(default: False)
--delete-records-on-moduli-write
Delete records on moduli write (default: False)
```

## Verify Database Configuration

Note: _On initial install, the stats will be empty_

```bash
((.venv) ) [MG_User@localhost ~/tmp/moduli_generator %] moduli_stats       [15:59:20]
Key-Length: #Records
3071: 3856
4095: 1012
6143: 734
7679: 349
8191: 376
available moduli files: 17

```