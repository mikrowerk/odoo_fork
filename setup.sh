#!/usr/bin/env bash
# SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source ./odoo_env/bin/activate
echo "using venv= $(which python)"
python3 -m pip install -r ./requirements.txt --upgrade

