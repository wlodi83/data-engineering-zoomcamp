#!/bin/bash
# Set up virtual environment for homework scripts
python3.12 -m venv --without-pip venv
source venv/bin/activate
python3.12 -m ensurepip --default-pip 2>/dev/null || true
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12
pip install -r requirements.txt
echo ""
echo "Done! Activate with: source venv/bin/activate"
