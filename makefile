
SHELL:=/bin/bash
ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

.PHONY: all fresh dependencies install fulluninstall uninstall removedeps

all: dependencies

fresh: fulluninstall dependencies

fulluninstall: uninstall cleancode

install:
	# Create link in /usr/local/bin to screeps stats program.
	ln -s -f $(ROOT_DIR)/bin/screeps_backup /usr/local/bin/screeps_backup
	ln -s -f $(ROOT_DIR)/bin/screeps_restore /usr/local/bin/screeps_restore

dependencies:
	if [ ! -d $(ROOT_DIR)/env ]; then virtualenv $(ROOT_DIR)/env; fi
	source $(ROOT_DIR)/env/bin/activate; yes w | pip install -r $(ROOT_DIR)/requirements.txt

uninstall:
	# Remove links in /user/local/bin
	if [ -L /usr/local/bin/screeps_backup ]; then \
		rm /usr/local/bin/screeps_backup; \
	fi;
	if [ -L /usr/local/bin/screeps_restore ]; then \
		rm /usr/local/bin/screeps_restore; \
	fi;

cleancode:
	# Remove existing environment
	if [ -d $(ROOT_DIR)/env ]; then \
		rm -rf $(ROOT_DIR)/env; \
	fi;
	# Remove compiled python files
	rm -f $(ROOT_DIR)/*.pyc; \
