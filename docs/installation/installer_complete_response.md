```bash
(.venv) [ron@aragorn ~ %] mkdir -p ~/moduli_generator                                                                                                                                                                               [11:36:58]
cd ~/moduli_generator
(.venv) [ron@aragorn ~/moduli_generator %] curl -fsSL -o install_mg.sh https://raw.githubusercontent.com/beckerwilliams/moduli_generator/HEAD/data/bash_scripts/install_mg.sh                                                       [11:37:51]
(.venv) [ron@aragorn ~/moduli_generator %] chmod +x ./install_mg.sh                                                                                                                                                                 [11:37:58]
./install_mg.sh
Project Name: moduli_generator
	WORK_DIR: .moduli_generator_build_env
	CWD: /Users/ron/moduli_generator
[ Verifying System Requirements ]
✓ Git is installed: git version 2.39.5 (Apple Git-154)
✓ Python 3.13 is installed (≥3.12 required): Python 3.13.6
✓ All requirements verified successfully
[ Database Configuration Setup ]
Please provide MariaDB connection details for the moduli_generator user:

\033[0;32mPlease collect the privilged MariaDB's account _username_ and _password_ for use, Now!\033[0m
Privilged MariaDB _username_ (i.e., an admin): ron

Enter password for ron: 
MariaDB hostname [localhost]: 
MariaDB port [3306]: 
Enable SSL [true]: 

Configuration Summary:
  User: ron
  SSL: true
  Host: localhost
  Port: 3306

Is this configuration correct? (y/n): y
✓ Configuration file created: /Users/ron/.moduli_generator/privileged.tmp
File permissions set to 600 (owner read/write only)
*** Project Name: moduli_generator
	WORK_DIR: .moduli_generator_build_env
	CWD: /Users/ron/moduli_generator ***
[ Saving Current Directory /Users/ron/moduli_generator, entering .moduli_generator_build_env ]
[ Cloning moduli_generator from Github ]
Cloning into 'moduli_generator'...
remote: Enumerating objects: 2006, done.
remote: Counting objects: 100% (120/120), done.
remote: Compressing objects: 100% (79/79), done.
remote: Total 2006 (delta 54), reused 68 (delta 41), pack-reused 1886 (from 1)
Receiving objects: 100% (2006/2006), 35.82 MiB | 69.08 MiB/s, done.
Resolving deltas: 100% (1220/1220), done.
[ Entering Moduli Dev Directory ]
✓ Poetry/PEP 621 project configuration found
[ Creating and Activating Moduli Generator's Wheel Builder ]
✓ Virtual environment activated
Using pip: /Users/ron/moduli_generator/.moduli_generator_build_env/moduli_generator/.venv/bin/pip --no-cache-dir
[ Upgrading pip ]
Requirement already satisfied: pip in ./.venv/lib/python3.13/site-packages (25.2)
[ Installing Poetry in virtual environment ]
Collecting poetry==1.8.3
  Downloading poetry-1.8.3-py3-none-any.whl.metadata (6.8 kB)
Collecting build<2.0.0,>=1.0.3 (from poetry==1.8.3)
  Downloading build-1.3.0-py3-none-any.whl.metadata (5.6 kB)
Collecting cachecontrol<0.15.0,>=0.14.0 (from cachecontrol[filecache]<0.15.0,>=0.14.0->poetry==1.8.3)
  Downloading cachecontrol-0.14.3-py3-none-any.whl.metadata (3.1 kB)
Collecting cleo<3.0.0,>=2.1.0 (from poetry==1.8.3)
  Downloading cleo-2.1.0-py3-none-any.whl.metadata (12 kB)
Collecting crashtest<0.5.0,>=0.4.1 (from poetry==1.8.3)
  Downloading crashtest-0.4.1-py3-none-any.whl.metadata (1.1 kB)
Collecting dulwich<0.22.0,>=0.21.2 (from poetry==1.8.3)
  Downloading dulwich-0.21.7.tar.gz (448 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting fastjsonschema<3.0.0,>=2.18.0 (from poetry==1.8.3)
  Downloading fastjsonschema-2.21.2-py3-none-any.whl.metadata (2.3 kB)
Collecting installer<0.8.0,>=0.7.0 (from poetry==1.8.3)
  Downloading installer-0.7.0-py3-none-any.whl.metadata (936 bytes)
Collecting keyring<25.0.0,>=24.0.0 (from poetry==1.8.3)
  Downloading keyring-24.3.1-py3-none-any.whl.metadata (20 kB)
Collecting packaging>=23.1 (from poetry==1.8.3)
  Downloading packaging-25.0-py3-none-any.whl.metadata (3.3 kB)
Collecting pexpect<5.0.0,>=4.7.0 (from poetry==1.8.3)
  Downloading pexpect-4.9.0-py2.py3-none-any.whl.metadata (2.5 kB)
Collecting pkginfo<2.0,>=1.10 (from poetry==1.8.3)
  Downloading pkginfo-1.12.1.2-py3-none-any.whl.metadata (13 kB)
Collecting platformdirs<5,>=3.0.0 (from poetry==1.8.3)
  Downloading platformdirs-4.3.8-py3-none-any.whl.metadata (12 kB)
Collecting poetry-core==1.9.0 (from poetry==1.8.3)
  Downloading poetry_core-1.9.0-py3-none-any.whl.metadata (3.5 kB)
Collecting poetry-plugin-export<2.0.0,>=1.6.0 (from poetry==1.8.3)
  Downloading poetry_plugin_export-1.9.0-py3-none-any.whl.metadata (3.1 kB)
Collecting pyproject-hooks<2.0.0,>=1.0.0 (from poetry==1.8.3)
  Downloading pyproject_hooks-1.2.0-py3-none-any.whl.metadata (1.3 kB)
Collecting requests<3.0,>=2.26 (from poetry==1.8.3)
  Downloading requests-2.32.4-py3-none-any.whl.metadata (4.9 kB)
Collecting requests-toolbelt<2.0.0,>=1.0.0 (from poetry==1.8.3)
  Downloading requests_toolbelt-1.0.0-py2.py3-none-any.whl.metadata (14 kB)
Collecting shellingham<2.0,>=1.5 (from poetry==1.8.3)
  Downloading shellingham-1.5.4-py2.py3-none-any.whl.metadata (3.5 kB)
Collecting tomlkit<1.0.0,>=0.11.4 (from poetry==1.8.3)
  Downloading tomlkit-0.13.3-py3-none-any.whl.metadata (2.8 kB)
Collecting trove-classifiers>=2022.5.19 (from poetry==1.8.3)
  Downloading trove_classifiers-2025.8.6.13-py3-none-any.whl.metadata (2.3 kB)
Collecting virtualenv<21.0.0,>=20.23.0 (from poetry==1.8.3)
  Downloading virtualenv-20.34.0-py3-none-any.whl.metadata (4.6 kB)
Collecting xattr<2.0.0,>=1.0.0 (from poetry==1.8.3)
  Downloading xattr-1.2.0-cp313-cp313-macosx_10_13_x86_64.whl.metadata (3.8 kB)
Collecting msgpack<2.0.0,>=0.5.2 (from cachecontrol<0.15.0,>=0.14.0->cachecontrol[filecache]<0.15.0,>=0.14.0->poetry==1.8.3)
  Downloading msgpack-1.1.1-cp313-cp313-macosx_10_13_x86_64.whl.metadata (8.4 kB)
Collecting filelock>=3.8.0 (from cachecontrol[filecache]<0.15.0,>=0.14.0->poetry==1.8.3)
  Downloading filelock-3.19.1-py3-none-any.whl.metadata (2.1 kB)
Collecting rapidfuzz<4.0.0,>=3.0.0 (from cleo<3.0.0,>=2.1.0->poetry==1.8.3)
  Downloading rapidfuzz-3.13.0-cp313-cp313-macosx_10_13_x86_64.whl.metadata (12 kB)
Collecting urllib3>=1.25 (from dulwich<0.22.0,>=0.21.2->poetry==1.8.3)
  Downloading urllib3-2.5.0-py3-none-any.whl.metadata (6.5 kB)
Collecting jaraco.classes (from keyring<25.0.0,>=24.0.0->poetry==1.8.3)
  Downloading jaraco.classes-3.4.0-py3-none-any.whl.metadata (2.6 kB)
Collecting ptyprocess>=0.5 (from pexpect<5.0.0,>=4.7.0->poetry==1.8.3)
  Downloading ptyprocess-0.7.0-py2.py3-none-any.whl.metadata (1.3 kB)
INFO: pip is looking at multiple versions of poetry-plugin-export to determine which version is compatible with other requirements. This could take a while.
Collecting poetry-plugin-export<2.0.0,>=1.6.0 (from poetry==1.8.3)
  Downloading poetry_plugin_export-1.8.0-py3-none-any.whl.metadata (2.8 kB)
Collecting charset_normalizer<4,>=2 (from requests<3.0,>=2.26->poetry==1.8.3)
  Downloading charset_normalizer-3.4.3-cp313-cp313-macosx_10_13_universal2.whl.metadata (36 kB)
Collecting idna<4,>=2.5 (from requests<3.0,>=2.26->poetry==1.8.3)
  Downloading idna-3.10-py3-none-any.whl.metadata (10 kB)
Collecting certifi>=2017.4.17 (from requests<3.0,>=2.26->poetry==1.8.3)
  Downloading certifi-2025.8.3-py3-none-any.whl.metadata (2.4 kB)
Collecting distlib<1,>=0.3.7 (from virtualenv<21.0.0,>=20.23.0->poetry==1.8.3)
  Downloading distlib-0.4.0-py2.py3-none-any.whl.metadata (5.2 kB)
Collecting cffi>=1.16.0 (from xattr<2.0.0,>=1.0.0->poetry==1.8.3)
  Downloading cffi-1.17.1-cp313-cp313-macosx_10_13_x86_64.whl.metadata (1.5 kB)
Collecting pycparser (from cffi>=1.16.0->xattr<2.0.0,>=1.0.0->poetry==1.8.3)
  Downloading pycparser-2.22-py3-none-any.whl.metadata (943 bytes)
Collecting more-itertools (from jaraco.classes->keyring<25.0.0,>=24.0.0->poetry==1.8.3)
  Downloading more_itertools-10.7.0-py3-none-any.whl.metadata (37 kB)
Downloading poetry-1.8.3-py3-none-any.whl (249 kB)
Downloading poetry_core-1.9.0-py3-none-any.whl (309 kB)
Downloading build-1.3.0-py3-none-any.whl (23 kB)
Downloading cachecontrol-0.14.3-py3-none-any.whl (21 kB)
Downloading cleo-2.1.0-py3-none-any.whl (78 kB)
Downloading crashtest-0.4.1-py3-none-any.whl (7.6 kB)
Downloading fastjsonschema-2.21.2-py3-none-any.whl (24 kB)
Downloading installer-0.7.0-py3-none-any.whl (453 kB)
Downloading keyring-24.3.1-py3-none-any.whl (38 kB)
Downloading msgpack-1.1.1-cp313-cp313-macosx_10_13_x86_64.whl (81 kB)
Downloading pexpect-4.9.0-py2.py3-none-any.whl (63 kB)
Downloading pkginfo-1.12.1.2-py3-none-any.whl (32 kB)
Downloading platformdirs-4.3.8-py3-none-any.whl (18 kB)
Downloading poetry_plugin_export-1.8.0-py3-none-any.whl (10 kB)
Downloading pyproject_hooks-1.2.0-py3-none-any.whl (10 kB)
Downloading rapidfuzz-3.13.0-cp313-cp313-macosx_10_13_x86_64.whl (2.0 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.0/2.0 MB 104.5 MB/s  0:00:00
Downloading requests-2.32.4-py3-none-any.whl (64 kB)
Downloading charset_normalizer-3.4.3-cp313-cp313-macosx_10_13_universal2.whl (205 kB)
Downloading idna-3.10-py3-none-any.whl (70 kB)
Downloading requests_toolbelt-1.0.0-py2.py3-none-any.whl (54 kB)
Downloading shellingham-1.5.4-py2.py3-none-any.whl (9.8 kB)
Downloading tomlkit-0.13.3-py3-none-any.whl (38 kB)
Downloading urllib3-2.5.0-py3-none-any.whl (129 kB)
Downloading virtualenv-20.34.0-py3-none-any.whl (6.0 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 6.0/6.0 MB 118.1 MB/s  0:00:00
Downloading distlib-0.4.0-py2.py3-none-any.whl (469 kB)
Downloading filelock-3.19.1-py3-none-any.whl (15 kB)
Downloading xattr-1.2.0-cp313-cp313-macosx_10_13_x86_64.whl (19 kB)
Downloading certifi-2025.8.3-py3-none-any.whl (161 kB)
Downloading cffi-1.17.1-cp313-cp313-macosx_10_13_x86_64.whl (182 kB)
Downloading packaging-25.0-py3-none-any.whl (66 kB)
Downloading ptyprocess-0.7.0-py2.py3-none-any.whl (13 kB)
Downloading trove_classifiers-2025.8.6.13-py3-none-any.whl (14 kB)
Downloading jaraco.classes-3.4.0-py3-none-any.whl (6.8 kB)
Downloading more_itertools-10.7.0-py3-none-any.whl (65 kB)
Downloading pycparser-2.22-py3-none-any.whl (117 kB)
Building wheels for collected packages: dulwich
  Building wheel for dulwich (pyproject.toml) ... done
  Created wheel for dulwich: filename=dulwich-0.21.7-cp313-cp313-macosx_15_0_x86_64.whl size=477902 sha256=870df458f1f2243a2a035239c8b70390684725866215cab5b5fdabc0c799f53c
  Stored in directory: /private/var/folders/0w/g13ncr2x1v1d717n0sbj35br0000gn/T/pip-ephem-wheel-cache-zddhytge/wheels/63/f9/68/6bb6145045043643aaf320f7e02bd693edd8db4a4e21472df8
Successfully built dulwich
Installing collected packages: trove-classifiers, ptyprocess, fastjsonschema, distlib, urllib3, tomlkit, shellingham, rapidfuzz, pyproject-hooks, pycparser, poetry-core, platformdirs, pkginfo, pexpect, packaging, msgpack, more-itertools, installer, idna, filelock, crashtest, charset_normalizer, certifi, virtualenv, requests, jaraco.classes, dulwich, cleo, cffi, build, xattr, requests-toolbelt, keyring, cachecontrol, poetry-plugin-export, poetry
Successfully installed build-1.3.0 cachecontrol-0.14.3 certifi-2025.8.3 cffi-1.17.1 charset_normalizer-3.4.3 cleo-2.1.0 crashtest-0.4.1 distlib-0.4.0 dulwich-0.21.7 fastjsonschema-2.21.2 filelock-3.19.1 idna-3.10 installer-0.7.0 jaraco.classes-3.4.0 keyring-24.3.1 more-itertools-10.7.0 msgpack-1.1.1 packaging-25.0 pexpect-4.9.0 pkginfo-1.12.1.2 platformdirs-4.3.8 poetry-1.8.3 poetry-core-1.9.0 poetry-plugin-export-1.8.0 ptyprocess-0.7.0 pycparser-2.22 pyproject-hooks-1.2.0 rapidfuzz-3.13.0 requests-2.32.4 requests-toolbelt-1.0.0 shellingham-1.5.4 tomlkit-0.13.3 trove-classifiers-2025.8.6.13 urllib3-2.5.0 virtualenv-20.34.0 xattr-1.2.0
Poetry (version 1.8.3)
✓ Poetry installed successfully: Poetry (version 1.8.3)
[ Installing project dependencies ]
Installing dependencies from lock file

Package operations: 42 installs, 2 updates, 0 removals

  - Installing six (1.17.0)
  - Installing mergedeep (1.3.4)
  - Installing markupsafe (3.0.2)
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
  - Installing colorama (0.4.6)
  - Installing iniconfig (2.1.0)
  - Installing mkdocs-autorefs (1.4.2)
  - Installing pluggy (1.6.0)
  - Updating poetry-core (1.9.0 -> 1.9.1)
  - Installing pygments (2.19.2)
  - Installing pymdown-extensions (10.16.1)
  - Installing pytest (8.4.1)
  - Installing mkdocstrings (0.30.0)
  - Installing coverage (7.10.3)
  - Installing babel (2.17.0)
  - Installing paginate (0.5.7)
  - Installing backrefs (5.9)
  - Installing setuptools (80.9.0)
  - Installing mkdocs-material-extensions (1.3.1)
  - Installing toml (0.10.2)
  - Installing wheel (0.45.1)
  - Installing griffe (1.12.1)
  - Installing mypy-extensions (1.1.0)
  - Installing black (25.1.0)
  - Installing configparser (7.2.0)
  - Installing pip-tools (7.5.0)
  - Installing pytest-cov (2.12.1)
  - Updating poetry (1.8.3 -> 1.8.5)
  - Installing mkdocstrings-python (1.16.12)
  - Installing mariadb (1.1.13)
  - Installing pytest-asyncio (1.1.0)
  - Installing mkdocs-material (9.6.16)
  - Installing pytest-mock (3.14.1)
  - Installing typing-extensions (4.14.1)

Installing the current project: moduli_generator (2.1.37)
[ Updating Poetry lock file ]
Resolving dependencies... (0.2s)
[ Building moduli_generator wheel ]
Building moduli_generator (2.1.37)
  - Building sdist
  - Built moduli_generator-2.1.37.tar.gz
  - Building wheel
  - Built moduli_generator-2.1.37-py3-none-any.whl
✓ Wheel file created: moduli_generator-2.1.37-py3-none-any.whl
[ Moduli Generator Wheel: /Users/ron/moduli_generator/moduli_generator-2.1.37-py3-none-any.whl ]
Deleted Temporary Work Dir: .moduli_generator_build_env
✓ Build wheel completed successfully
*** Project Name: moduli_generator
	WORK_DIR: .moduli_generator_build_env
	CWD: /Users/ron/moduli_generator ***
[ Cleaning up existing runtime virtual environment ]
[ Creating runtime virtual environment ]
✓ Virtual environment activated
Using pip: /Users/ron/moduli_generator/.venv/bin/pip --no-cache-dir
[ Upgrading Virtual Environment and Installing Moduli Generator wheel ]
Requirement already satisfied: pip in ./.venv/lib/python3.13/site-packages (25.2)
Processing ./moduli_generator-2.1.37-py3-none-any.whl
Collecting configparser>=7.2.0 (from moduli-generator==2.1.37)
  Downloading configparser-7.2.0-py3-none-any.whl.metadata (5.5 kB)
Collecting mariadb==1.1.13 (from moduli-generator==2.1.37)
  Downloading mariadb-1.1.13.tar.gz (111 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting typing-extensions<5.0.0,>=4.14.1 (from moduli-generator==2.1.37)
  Downloading typing_extensions-4.14.1-py3-none-any.whl.metadata (3.0 kB)
Collecting packaging (from mariadb==1.1.13->moduli-generator==2.1.37)
  Downloading packaging-25.0-py3-none-any.whl.metadata (3.3 kB)
Downloading typing_extensions-4.14.1-py3-none-any.whl (43 kB)
Downloading configparser-7.2.0-py3-none-any.whl (17 kB)
Downloading packaging-25.0-py3-none-any.whl (66 kB)
Building wheels for collected packages: mariadb
  Building wheel for mariadb (pyproject.toml) ... done
  Created wheel for mariadb: filename=mariadb-1.1.13-cp313-cp313-macosx_15_0_x86_64.whl size=84368 sha256=7ee887ce075da13777b5d4adc7b71764dd567dbc9026545dab4a4849c47dd1e9
  Stored in directory: /private/var/folders/0w/g13ncr2x1v1d717n0sbj35br0000gn/T/pip-ephem-wheel-cache-ip46b2nb/wheels/75/17/95/111451bb9ffda683d39a782350e23086230e9583c8e9246c80
Successfully built mariadb
Installing collected packages: typing-extensions, packaging, configparser, mariadb, moduli-generator
Successfully installed configparser-7.2.0 mariadb-1.1.13 moduli-generator-2.1.37 packaging-25.0 typing-extensions-4.14.1
[ Moduli Generator Installed Successfully ]
Virtual Environment Package Manifest:
Package           Version
----------------- -------
configparser      7.2.0
mariadb           1.1.13
moduli_generator  2.1.37
packaging         25.0
pip               25.2
typing_extensions 4.14.1

✓ Runtime installation completed successfully
Installing schema for database: moduli_db with MariaDB config file: /Users/ron/.moduli_generator/privileged.tmp
Installing schema for database: moduli_db
Executing statement 1/10: CREATE DATABASE IF NOT EXISTS moduli_db...
Executing statement 2/10: CREATE TABLE moduli_db.mod_fl_consts (
           ...
Executing statement 3/10: CREATE TABLE IF NOT EXISTS moduli_db.moduli (
    ...
Executing statement 4/10: CREATE VIEW IF NOT EXISTS moduli_db.moduli_view AS...
Executing statement 5/10: CREATE TABLE IF NOT EXISTS moduli_db.moduli_archiv...
Executing statement 6/10: CREATE INDEX idx_size ON moduli_db.moduli(size)...
Executing statement 7/10: CREATE INDEX idx_timestamp ON moduli_db.moduli(tim...
Executing statement 8/10: CREATE INDEX idx_size ON moduli_db.moduli_archive(...
Executing statement 9/10: CREATE INDEX idx_timestamp ON moduli_db.moduli_arc...
Executing statement 10/10: INSERT INTO moduli_db.mod_fl_consts (config_id, ty...
Schema installation completed successfully
Database schema installed successfully

Creating moduli_generator user and finalizing configuration...
Executed: CREATE USER IF NOT EXISTS 'moduli_generator'@'%' I...
Executed: GRANT ALL PRIVILEGES ON moduli_db.* TO 'moduli_gen...
Executed: GRANT PROXY ON ''@'%' TO 'moduli_generator'@'%'...
Executed: FLUSH PRIVILEGES...
Executed: CREATE USER IF NOT EXISTS 'moduli_generator'@'loca...
Executed: GRANT ALL PRIVILEGES ON moduli_db.* TO 'moduli_gen...
Executed: FLUSH PRIVILEGES...
Created 'moduli_generator' user with access to 'moduli_db' database
Updated configuration file: /Users/ron/.moduli_generator/privileged.tmp
Successfully created moduli_generator user and updated configuration at /Users/ron/.moduli_generator/privileged.tmp
✓ Installation completed successfully!
To activate the environment, run: source .venv/bin/activate
To test the installation, run: moduli_generator --help
(.venv) [ron@aragorn ~/moduli_generator %]                                                                                                                                                                                          [11:39:29]

```