# SSH2 Moduli File Generator

Scripts to generate well constructed moduli file

            /etc/ssh/moduli | /usr/local/etc/ssh/moduli | 'ssh-moduli' | ...

## Table of Contents

### [Platform Dependencies](#platform-dependencies)

### [Installation](#installation)

### [Usage](#usage)

### [Utility Scripts](#utility-scripts)

### [License](#mit-license)

- OpenSSH2 ssh-keygen, _supports `-M generate` and `-M screen`_

- Python version >=3.7

- OpenSSH version >=9.7p1

- OpenSSL version >=3.0.14

## Overview

OpenSSH2 provides moduli generation capabilities via on platform `OpenSSH ssh-keygen`.
Rather than individually generating moduli across desired moduli key sizes, `SSH Moduli Generator` provides the means to
generate a complete moduli file with similar distributions across moduli.
Each run of ssh-keygen will produce about 25% of the moduli needed for a complete file. The included scripts,
`export_bash_builder` and `export_csh_builder`, will launch 4 runs of `moduli-assembly` in parallel, sufficient to
produce a complete ssh moduli file.

Note: _Elapsed time for complete run is about 7 **days** on an Intel Quad Core i7_

### Capabilities

Builds Complete file With One Command

- python: `python -m moduli_assembly --all`

Provides Scripts for managing parallel build of moduli

- bash: `python -m moduli.scripts.export_bash_runner > moduli_runner.sh`


- csh: `python -m moduli.scripts.export_csh_runner > moduli_runner.csh`


- set execute bit: `chmod +x moduli_runner.*sh`


- build moduli file: `./moduli_runner.[c]sh&`

## Installation

### Platform Dependencies

SSH2 Moduli Generator depends on the SSH being installed and ssh-keygen available for Moduli production.

### Install Wheel

In a working directory, Create a python virtual environment, install ssh-moduli-builder wheel, run.

- Create Virtual Environment
    - `python -m venv .venv  # Create Virtual Environment`

- Activate
    - Bash:    `source .venv/bin/activate.sh`
    - C-Shell: `source .venv/bin/activate.csh`

- Install Wheel
    - `pip install ./moduli_assembly-<version>-py3-none-any.whl`

## Usage

### --all, -a

Produce One Full Moduli Set

`python -m moduli_assembly --all`

_Builds SSH Moduli File with All Authorized Bitsizes:_

- _3071, 4095, 6143, 7679, 8191`_

### --bitsizes, -b

Produces Moduli with Selected Bitsizes

`python -m moduli_assembly --bitsizes <bitsize> [<bitsize> [...]]`

_Build Moduli for each bitsize given. Multiple Entries provide Multiple Runs_

Example

`python -m moduli_assembly --bitsizes 3072 3072 4096`

- _Two Runs of `3072`, one of `4096`_

### --restart, -r

Restart previously interrupted Screening Run

Example

`python -m moduli_assembly --restart`

- _Completes Screening of Any Interrupted Screening Runs_

### --write, -w

Example

`python -m moduli_assembly --write`

- _Writes out SSH MODULI File from Existing Safe Primes_

### --clear_artifacts, -c

Example

`python -m moduli_assembly --clear-artifacts`

* Clears candidate, candidate checkpoint, and screened moduli files from ${MODULI_DIR}

## Utility Scripts

In order to build a sufficiently diverse SSH Moduli file, we need 4 runs of EACH bitsize.
The following Shell Scripts will start 4 process in parallel, and produce a Complete SSH Moduli File with over
75 entries for each bitsize.

`moduli-assembly` will take about 1 Week to produce a complete File on an 4 Core Intel i7 processor.

### Export Shell Scripts

#### C Shell (csh) Moduli Runner

`python -m moduli_assembly.scripts.export_csh_runner > build_moduli_file.csh`

#### Bourne Again Shell (bash) Moduli Runner

`python -m moduli_assembly.scripts.export_bash_runner > build_moduli_file.sh`

#### Set the `exec` bit on Scripts

`chmod +x ./build_moduli_file.*sh`

### Build Complete Moduli File

_Note: This takes about 7 Days on a Quad Core Intel i7_

#### bash (sh)

`./build_moduli_file.sh > all.gen.log 2>&1 &`

#### c-shell (csh)

`./build_moduli_file.csh`

Log File `all.gen.log`

### Moduli Frequency Distribution

`moduli-assembly` provides in module and an exportable bash script that will display the frequency of the moduli in any
ssh moduli file.

#### Export moduli_infile script and exec enable

`python -m moduli_assembly.scripts.export_moduli_infile > moduli_infile.sh`

Set exec bit on shell script: `chmod +x ./moduli_infile.sh`

#### Moduli Infile Usage

##### Bash Script

`./moduli_infile.sh  # default moduli file /etc/ssh/moduli  # default`

or

`./moduli_infile.sh <MODULI_INFILE>` # default moduli file /etc/ssh/moduli # default

##### moduli-assembly

`python -m moduli_assembly.scripts.moduli_infile # default: /etc/ssh/moduli`

or

`python -m moduli_assembly.scripts.moduli_infile [-f <SSH_MODULI_FILE>]  # selected moduli file`

* Where default MODULI File is `/etc/ssh/moduli`

###### Moduli Infile Response

Modulus Frequency of /etc/ssh/moduli:

    Mod  Count
    3071 80
    4095 94
    6143 87
    7679 108
    8191 117

#### Retrieve last generated MODULI file

`python -m moduli_assembly.scripts.export_moduli_infile > MODULI_FILE`

### Use Moduli File

Locate your OpenSSH MODULI File

- /etc/ssh/moduli
- /usr/local/etc/moduli
- etc.

#### Export and Apply resulting MODULI FILE to Distribution

`cp ssh-moduli /etc/ssh/moduli`

or

`cp ssh-moduli /usr/local/etc/ssh/moduli`

#### That's It!

## Reference

### SSH Audit

[SSH Audit](https://github.com/jtesta/ssh-audit)

### SSH Hardening Guides

[SSH Hardening Guides](https://www.ssh-audit.com/hardening_guides.html)

### HackTricks (SSH)

[HackTricks](https://book.hacktricks.xyz/network-services-pentesting/pentesting-ssh)

## License

### MIT License

[MIT License](#LICENSE)

#Copyright (c) 2024, 2025 Ron Williams, General Partner, Becker Williams Trading General Partnership

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
