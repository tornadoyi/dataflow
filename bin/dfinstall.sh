# !! NOTICE !!
# THIS FILE IS ONLY SCRIPT SOURCE FOR DEPLOY AND IT IS DOES NOT WORK WITHOUT COMPILING ON GIT ACCESS MODE

#!/bin/bash

# uninstall
pip uninstall dataflow -y

# install
pip install git+ssh://git@git.corpautohome.com/autorcm/dataflow.git