#!/usr/bin/env bash

source venv/bin/activate

pip install sphinx

PYTHONPATH=. sphinx-apidoc -e -f -o sphinx-docs/source riscemu riscemu/colors.py riscemu/__main__.py

cd sphinx-docs

make html

# xdg-open build/html/index.html