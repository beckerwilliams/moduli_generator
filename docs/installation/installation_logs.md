# Installation Logs

## git-install.log

```bash
Cloning into 'moduli_generator'...
```

## poetry-install.log

```bash
Poetry (version 1.8.3)
Installing dependencies from lock file

Package operations: 42 installs, 2 updates, 0 removals

  - Installing six (1.17.0)
  - Installing markupsafe (3.0.2)
  - Installing mergedeep (1.3.4)
  - Installing python-dateutil (2.9.0.post0)
  - Installing pyyaml (6.0.2)
  - Installing click (8.2.1)
  - Installing ghp-import (2.1.0)
  - Installing markdown (3.8.2)
  - Installing jinja2 (3.1.6)
  - Installing pyyaml-env-tag (1.1)
  - Installing watchdog (6.0.0)
  - Installing mkdocs-get-deps (0.2.0)
  - Installing pathspec (0.12.1)
  - Installing mkdocs (1.6.1)
  - Installing colorama (0.4.6)
  - Installing iniconfig (2.1.0)
  - Installing pluggy (1.6.0)
  - Installing pygments (2.19.2)
  - Installing mkdocs-autorefs (1.4.2)
  - Updating poetry-core (1.9.0 -> 1.9.1)
  - Installing pymdown-extensions (10.16.1)
  - Installing pytest (8.4.1)
  - Installing mkdocs-material-extensions (1.3.1)
  - Installing paginate (0.5.7)
  - Installing mkdocstrings (0.30.0)
  - Installing backrefs (5.9)
  - Installing griffe (1.12.1)
  - Installing mypy-extensions (1.1.0)
  - Installing coverage (7.10.4)
  - Installing setuptools (80.9.0)
  - Installing babel (2.17.0)
  - Installing toml (0.10.2)
  - Installing wheel (0.45.1)
  - Installing configparser (7.2.0)
  - Installing pip-tools (7.5.0)
  - Installing mkdocs-material (9.6.17)
  - Installing black (25.1.0)
  - Installing pytest-cov (2.12.1)
  - Installing pytest-asyncio (1.1.0)
  - Installing mkdocstrings-python (1.16.12)
  - Installing mariadb (1.1.13)
  - Installing pytest-mock (3.14.1)
  - Updating poetry (1.8.3 -> 1.8.5)
  - Installing typing-extensions (4.14.1)

Installing the current project: moduli_generator (1.0.1)
Resolving dependencies...
Building moduli_generator (1.0.1)
  - Building sdist
  - Built moduli_generator-1.0.1.tar.gz
  - Building wheel
  - Built moduli_generator-1.0.1-py3-none-any.whl
```

## pip-install.log

```bash
Requirement already satisfied: pip in ./.venv/lib/python3.13/site-packages (25.2)
WARNING: Skipping poetry as it is not installed.
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
  Using cached dulwich-0.21.7-cp313-cp313-macosx_15_0_x86_64.whl
Collecting fastjsonschema<3.0.0,>=2.18.0 (from poetry==1.8.3)
  Using cached fastjsonschema-2.21.2-py3-none-any.whl.metadata (2.3 kB)
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
  Using cached requests-2.32.5-py3-none-any.whl.metadata (4.9 kB)
Collecting requests-toolbelt<2.0.0,>=1.0.0 (from poetry==1.8.3)
  Using cached requests_toolbelt-1.0.0-py2.py3-none-any.whl.metadata (14 kB)
Collecting shellingham<2.0,>=1.5 (from poetry==1.8.3)
  Using cached shellingham-1.5.4-py2.py3-none-any.whl.metadata (3.5 kB)
Collecting tomlkit<1.0.0,>=0.11.4 (from poetry==1.8.3)
  Using cached tomlkit-0.13.3-py3-none-any.whl.metadata (2.8 kB)
Collecting trove-classifiers>=2022.5.19 (from poetry==1.8.3)
  Using cached trove_classifiers-2025.8.6.13-py3-none-any.whl.metadata (2.3 kB)
Collecting virtualenv<21.0.0,>=20.23.0 (from poetry==1.8.3)
  Using cached virtualenv-20.34.0-py3-none-any.whl.metadata (4.6 kB)
Collecting xattr<2.0.0,>=1.0.0 (from poetry==1.8.3)
  Using cached xattr-1.2.0-cp313-cp313-macosx_10_13_x86_64.whl.metadata (3.8 kB)
Collecting msgpack<2.0.0,>=0.5.2 (from cachecontrol<0.15.0,>=0.14.0->cachecontrol[filecache]<0.15.0,>=0.14.0->poetry==1.8.3)
  Using cached msgpack-1.1.1-cp313-cp313-macosx_10_13_x86_64.whl.metadata (8.4 kB)
Collecting filelock>=3.8.0 (from cachecontrol[filecache]<0.15.0,>=0.14.0->poetry==1.8.3)
  Using cached filelock-3.19.1-py3-none-any.whl.metadata (2.1 kB)
Collecting rapidfuzz<4.0.0,>=3.0.0 (from cleo<3.0.0,>=2.1.0->poetry==1.8.3)
  Using cached rapidfuzz-3.13.0-cp313-cp313-macosx_10_13_x86_64.whl.metadata (12 kB)
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
  Using cached charset_normalizer-3.4.3-cp313-cp313-macosx_10_13_universal2.whl.metadata (36 kB)
Collecting idna<4,>=2.5 (from requests<3.0,>=2.26->poetry==1.8.3)
  Using cached idna-3.10-py3-none-any.whl.metadata (10 kB)
Collecting certifi>=2017.4.17 (from requests<3.0,>=2.26->poetry==1.8.3)
  Using cached certifi-2025.8.3-py3-none-any.whl.metadata (2.4 kB)
Collecting distlib<1,>=0.3.7 (from virtualenv<21.0.0,>=20.23.0->poetry==1.8.3)
  Using cached distlib-0.4.0-py2.py3-none-any.whl.metadata (5.2 kB)
Collecting cffi>=1.16.0 (from xattr<2.0.0,>=1.0.0->poetry==1.8.3)
  Using cached cffi-1.17.1-cp313-cp313-macosx_10_13_x86_64.whl.metadata (1.5 kB)
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
Using cached fastjsonschema-2.21.2-py3-none-any.whl (24 kB)
Using cached installer-0.7.0-py3-none-any.whl (453 kB)
Using cached keyring-24.3.1-py3-none-any.whl (38 kB)
Using cached msgpack-1.1.1-cp313-cp313-macosx_10_13_x86_64.whl (81 kB)
Using cached pexpect-4.9.0-py2.py3-none-any.whl (63 kB)
Using cached pkginfo-1.12.1.2-py3-none-any.whl (32 kB)
Using cached platformdirs-4.3.8-py3-none-any.whl (18 kB)
Using cached poetry_plugin_export-1.8.0-py3-none-any.whl (10 kB)
Using cached pyproject_hooks-1.2.0-py3-none-any.whl (10 kB)
Using cached rapidfuzz-3.13.0-cp313-cp313-macosx_10_13_x86_64.whl (2.0 MB)
Using cached requests-2.32.5-py3-none-any.whl (64 kB)
Using cached charset_normalizer-3.4.3-cp313-cp313-macosx_10_13_universal2.whl (205 kB)
Using cached idna-3.10-py3-none-any.whl (70 kB)
Using cached requests_toolbelt-1.0.0-py2.py3-none-any.whl (54 kB)
Using cached shellingham-1.5.4-py2.py3-none-any.whl (9.8 kB)
Using cached tomlkit-0.13.3-py3-none-any.whl (38 kB)
Using cached urllib3-2.5.0-py3-none-any.whl (129 kB)
Using cached virtualenv-20.34.0-py3-none-any.whl (6.0 MB)
Using cached distlib-0.4.0-py2.py3-none-any.whl (469 kB)
Using cached filelock-3.19.1-py3-none-any.whl (15 kB)
Using cached xattr-1.2.0-cp313-cp313-macosx_10_13_x86_64.whl (19 kB)
Using cached certifi-2025.8.3-py3-none-any.whl (161 kB)
Using cached cffi-1.17.1-cp313-cp313-macosx_10_13_x86_64.whl (182 kB)
Using cached packaging-25.0-py3-none-any.whl (66 kB)
Using cached ptyprocess-0.7.0-py2.py3-none-any.whl (13 kB)
Using cached trove_classifiers-2025.8.6.13-py3-none-any.whl (14 kB)
Using cached jaraco.classes-3.4.0-py3-none-any.whl (6.8 kB)
Using cached more_itertools-10.7.0-py3-none-any.whl (65 kB)
Using cached pycparser-2.22-py3-none-any.whl (117 kB)
Installing collected packages: trove-classifiers, ptyprocess, fastjsonschema, distlib, urllib3, tomlkit, shellingham, rapidfuzz, pyproject-hooks, pycparser, poetry-core, platformdirs, pkginfo, pexpect, packaging, msgpack, more-itertools, installer, idna, filelock, crashtest, charset_normalizer, certifi, virtualenv, requests, jaraco.classes, dulwich, cleo, cffi, build, xattr, requests-toolbelt, keyring, cachecontrol, poetry-plugin-export, poetry

Successfully installed build-1.3.0 cachecontrol-0.14.3 certifi-2025.8.3 cffi-1.17.1 charset_normalizer-3.4.3 cleo-2.1.0 crashtest-0.4.1 distlib-0.4.0 dulwich-0.21.7 fastjsonschema-2.21.2 filelock-3.19.1 idna-3.10 installer-0.7.0 jaraco.classes-3.4.0 keyring-24.3.1 more-itertools-10.7.0 msgpack-1.1.1 packaging-25.0 pexpect-4.9.0 pkginfo-1.12.1.2 platformdirs-4.3.8 poetry-1.8.3 poetry-core-1.9.0 poetry-plugin-export-1.8.0 ptyprocess-0.7.0 pycparser-2.22 pyproject-hooks-1.2.0 rapidfuzz-3.13.0 requests-2.32.5 requests-toolbelt-1.0.0 shellingham-1.5.4 tomlkit-0.13.3 trove-classifiers-2025.8.6.13 urllib3-2.5.0 virtualenv-20.34.0 xattr-1.2.0
Requirement already satisfied: pip in ./.venv/lib/python3.13/site-packages (25.2)
Processing ./moduli_generator-1.0.1-py3-none-any.whl
Collecting configparser>=7.2.0 (from moduli-generator==1.0.1)
  Using cached configparser-7.2.0-py3-none-any.whl.metadata (5.5 kB)
Collecting mariadb==1.1.13 (from moduli-generator==1.0.1)
  Using cached mariadb-1.1.13-cp313-cp313-macosx_15_0_x86_64.whl
Collecting mkdocs<2.0.0,>=1.6.1 (from moduli-generator==1.0.1)
  Using cached mkdocs-1.6.1-py3-none-any.whl.metadata (6.0 kB)
Collecting typing-extensions<5.0.0,>=4.14.1 (from moduli-generator==1.0.1)
  Using cached typing_extensions-4.14.1-py3-none-any.whl.metadata (3.0 kB)
Collecting packaging (from mariadb==1.1.13->moduli-generator==1.0.1)
  Using cached packaging-25.0-py3-none-any.whl.metadata (3.3 kB)
Collecting click>=7.0 (from mkdocs<2.0.0,>=1.6.1->moduli-generator==1.0.1)
  Using cached click-8.2.1-py3-none-any.whl.metadata (2.5 kB)
Collecting ghp-import>=1.0 (from mkdocs<2.0.0,>=1.6.1->moduli-generator==1.0.1)
  Using cached ghp_import-2.1.0-py3-none-any.whl.metadata (7.2 kB)
Collecting jinja2>=2.11.1 (from mkdocs<2.0.0,>=1.6.1->moduli-generator==1.0.1)
  Using cached jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
Collecting markdown>=3.3.6 (from mkdocs<2.0.0,>=1.6.1->moduli-generator==1.0.1)
  Using cached markdown-3.8.2-py3-none-any.whl.metadata (5.1 kB)
Collecting markupsafe>=2.0.1 (from mkdocs<2.0.0,>=1.6.1->moduli-generator==1.0.1)
  Using cached MarkupSafe-3.0.2-cp313-cp313-macosx_10_13_universal2.whl.metadata (4.0 kB)
Collecting mergedeep>=1.3.4 (from mkdocs<2.0.0,>=1.6.1->moduli-generator==1.0.1)
  Using cached mergedeep-1.3.4-py3-none-any.whl.metadata (4.3 kB)
Collecting mkdocs-get-deps>=0.2.0 (from mkdocs<2.0.0,>=1.6.1->moduli-generator==1.0.1)
  Using cached mkdocs_get_deps-0.2.0-py3-none-any.whl.metadata (4.0 kB)
Collecting pathspec>=0.11.1 (from mkdocs<2.0.0,>=1.6.1->moduli-generator==1.0.1)
  Using cached pathspec-0.12.1-py3-none-any.whl.metadata (21 kB)
Collecting pyyaml-env-tag>=0.1 (from mkdocs<2.0.0,>=1.6.1->moduli-generator==1.0.1)
  Using cached pyyaml_env_tag-1.1-py3-none-any.whl.metadata (5.5 kB)
Collecting pyyaml>=5.1 (from mkdocs<2.0.0,>=1.6.1->moduli-generator==1.0.1)
  Using cached PyYAML-6.0.2-cp313-cp313-macosx_10_13_x86_64.whl.metadata (2.1 kB)
Collecting watchdog>=2.0 (from mkdocs<2.0.0,>=1.6.1->moduli-generator==1.0.1)
  Using cached watchdog-6.0.0-cp313-cp313-macosx_10_13_x86_64.whl.metadata (44 kB)
Collecting python-dateutil>=2.8.1 (from ghp-import>=1.0->mkdocs<2.0.0,>=1.6.1->moduli-generator==1.0.1)
  Using cached python_dateutil-2.9.0.post0-py2.py3-none-any.whl.metadata (8.4 kB)
Collecting platformdirs>=2.2.0 (from mkdocs-get-deps>=0.2.0->mkdocs<2.0.0,>=1.6.1->moduli-generator==1.0.1)
  Using cached platformdirs-4.3.8-py3-none-any.whl.metadata (12 kB)
Collecting six>=1.5 (from python-dateutil>=2.8.1->ghp-import>=1.0->mkdocs<2.0.0,>=1.6.1->moduli-generator==1.0.1)
  Using cached six-1.17.0-py2.py3-none-any.whl.metadata (1.7 kB)
Using cached mkdocs-1.6.1-py3-none-any.whl (3.9 MB)
Using cached typing_extensions-4.14.1-py3-none-any.whl (43 kB)
Using cached click-8.2.1-py3-none-any.whl (102 kB)
Using cached configparser-7.2.0-py3-none-any.whl (17 kB)
Using cached ghp_import-2.1.0-py3-none-any.whl (11 kB)
Using cached jinja2-3.1.6-py3-none-any.whl (134 kB)
Using cached markdown-3.8.2-py3-none-any.whl (106 kB)
Using cached MarkupSafe-3.0.2-cp313-cp313-macosx_10_13_universal2.whl (14 kB)
Using cached mergedeep-1.3.4-py3-none-any.whl (6.4 kB)
Using cached mkdocs_get_deps-0.2.0-py3-none-any.whl (9.5 kB)
Using cached packaging-25.0-py3-none-any.whl (66 kB)
Using cached pathspec-0.12.1-py3-none-any.whl (31 kB)
Using cached platformdirs-4.3.8-py3-none-any.whl (18 kB)
Using cached python_dateutil-2.9.0.post0-py2.py3-none-any.whl (229 kB)
Using cached PyYAML-6.0.2-cp313-cp313-macosx_10_13_x86_64.whl (181 kB)
Using cached pyyaml_env_tag-1.1-py3-none-any.whl (4.7 kB)
Using cached six-1.17.0-py2.py3-none-any.whl (11 kB)
Using cached watchdog-6.0.0-cp313-cp313-macosx_10_13_x86_64.whl (88 kB)
Installing collected packages: watchdog, typing-extensions, six, pyyaml, platformdirs, pathspec, packaging, mergedeep, markupsafe, markdown, configparser, click, pyyaml-env-tag, python-dateutil, mkdocs-get-deps, mariadb, jinja2, ghp-import, mkdocs, moduli-generator

Successfully installed click-8.2.1 configparser-7.2.0 ghp-import-2.1.0 jinja2-3.1.6 mariadb-1.1.13 markdown-3.8.2 markupsafe-3.0.2 mergedeep-1.3.4 mkdocs-1.6.1 mkdocs-get-deps-0.2.0 moduli-generator-1.0.1 packaging-25.0 pathspec-0.12.1 platformdirs-4.3.8 python-dateutil-2.9.0.post0 pyyaml-6.0.2 pyyaml-env-tag-1.1 six-1.17.0 typing-extensions-4.14.1 watchdog-6.0.0
Package           Version
----------------- -----------
click             8.2.1
configparser      7.2.0
ghp-import        2.1.0
Jinja2            3.1.6
mariadb           1.1.13
Markdown          3.8.2
MarkupSafe        3.0.2
mergedeep         1.3.4
mkdocs            1.6.1
mkdocs-get-deps   0.2.0
moduli_generator  1.0.1
packaging         25.0
pathspec          0.12.1
pip               25.2
platformdirs      4.3.8
python-dateutil   2.9.0.post0
PyYAML            6.0.2
pyyaml_env_tag    1.1
six               1.17.0
typing_extensions 4.14.1
watchdog          6.0.0

```
