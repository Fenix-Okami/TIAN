#!/bin/bash

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Clone the HSK-3.0 repository into the data folder
git clone https://github.com/krmanik/HSK-3.0.git references/HSK-3.0