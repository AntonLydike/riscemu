#!/usr/bin/env bash
# super hacky script to generate documentation when developing and for readthedocs

echo "Generating docs!"

if command -v 'sphinx-apidoc' >/dev/null; then
  source venv/bin/activate
  pip install sphinx
fi

if [[ $1 == 'generate' ]]; then

  PYTHONPATH=../../ sphinx-apidoc -e -f -o . ../../riscemu ../../riscemu/colors.py ../../riscemu/__main__.py
  echo "only generating, not building..."
  exit 0
fi

PYTHONPATH=. sphinx-apidoc -e -f -o sphinx-docs/source riscemu riscemu/colors.py riscemu/__main__.py

cd sphinx-docs

make html

# xdg-open build/html/index.html