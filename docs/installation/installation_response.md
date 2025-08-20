### intallation response

```bash
(.venv) [ron@aragorn ~/moduli %] curl -fsSL -o install_mg.sh https://raw.githubusercontent.com/beckerwilliams/moduli_generator/HEAD/data/bash_scripts/install_mg.sh
(.venv) [ron@aragorn ~/moduli %] chmod +x ./install_mg.sh                                                                              [15:37:59]
./install_mg.sh
 Project Name: moduli_generator
	WORK_DIR: .moduli_generator_build_env
	CWD: /Users/ron/moduli
[ Verifying System Requirements ]
✓ Git is installed: git version 2.39.5 (Apple Git-154)
✓ Python 3.13 is installed (≥3.12 required): Python 3.13.6
✓ All requirements verified successfully
[ Database Configuration Setup ]
Please choose how you would like to provide MariaDB connection details:

1) Enter username and password
2) Use existing mariadb.cnf file
Please select an option (1-2): 2

Please provide your MariaDB configuration file for the moduli_generator installation:

Enter the path to your mariadb.cnf file: ../DOT_CNF/localhost.cnf

Configuration File: ../DOT_CNF/localhost.cnf

Is this configuration file correct? (y/n): y
✓ Configuration file copied to: /Users/ron/.moduli_generator/privileged.tmp
File permissions set to 600 (owner read/write only)
*** Project Name: moduli_generator
	WORK_DIR: .moduli_generator_build_env
	CWD: /Users/ron/moduli ***
[ Saving Current Directory /Users/ron/moduli, entering .moduli_generator_build_env ]
[ Cloning moduli_generator from Github ]
Git clone output has been logged to /Users/ron/moduli/git-install.log
[ Entering Moduli Dev Directory ]
✓ Poetry/PEP 621 project configuration found
[ Creating and Activating Moduli Generator\'s Wheel Builder ]
✓ Virtual environment activated
Using pip: /Users/ron/moduli/.moduli_generator_build_env/moduli_generator/.venv/bin/pip
[ Upgrading pip ]
[ Installing Poetry in virtual environment ]
✓ Poetry installed successfully
[ Installing project dependencies ]
Poetry installation output has been logged to /Users/ron/moduli/poetry-install.log
[ Updating Poetry lock file ]
Poetry lock output has been logged to /Users/ron/moduli/poetry-install.log
[ Building moduli_generator wheel ]
Poetry build output has been logged to /Users/ron/moduli/poetry-install.log
✓ Wheel file created: moduli_generator-1.0.1-py3-none-any.whl
[ Moduli Generator Wheel: /Users/ron/moduli/moduli_generator-1.0.1-py3-none-any.whl ]
Deleted Temporary Work Dir: .moduli_generator_build_env
✓ Build wheel completed successfully
*** Project Name: moduli_generator
	WORK_DIR: .moduli_generator_build_env
	CWD: /Users/ron/moduli ***
[ Creating runtime virtual environment ]
✓ Virtual environment activated
Using pip: /Users/ron/moduli/.venv/bin/pip
[ Upgrading Virtual Environment and Installing Moduli Generator wheel ]
[ Moduli Generator Installed Successfully ]
Virtual Environment Package Manifest:
Package manifest has been logged to /Users/ron/moduli/pip-install.log

 ✓ Runtime installation completed successfully 
✓ Virtual environment activated
Using pip: /Users/ron/moduli/.venv/bin/pip
Installing schema for database: moduli_db
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
Executing statement 1/6: CREATE USER IF NOT EXISTS 'moduli_generator'@'%' I...
Executing statement 2/6: GRANT ALL PRIVILEGES ON moduli_db.* TO 'moduli_gen...
Executing statement 3/6: FLUSH PRIVILEGES...
Executing statement 4/6: CREATE USER IF NOT EXISTS 'moduli_generator'@'loca...
Executing statement 5/6: GRANT ALL PRIVILEGES ON moduli_db.* TO 'moduli_gen...
Executing statement 6/6: FLUSH PRIVILEGES...
Schema installation completed successfully
Database and User schema installed successfully
 ✓ Installation completed successfully! 
 To activate the environment, run: source .venv/bin/activate 
 To test the installation, run: moduli_generator --help 
 
```
