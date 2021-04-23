#!/usr/bin/env bash
# super hacky script to generate documentation when developing and for readthedocs

echo "Generating docs!"


if ! command -v 'sphinx-apidoc'; then
  source venv/bin/activate
  pip install sphinx
fi



if [[ $1 == 'generate' ]]; then

  # delete old help folder
  rm -rf help
  cp -r ../../docs help

  PYTHONPATH=../../ sphinx-apidoc -e -f -o . ../../riscemu ../../riscemu/colors.py ../../riscemu/__main__.py
  echo "only generating, not building..."
  rm ./modules.rst
  exit 0
fi

# delete old help folder
rm -rf sphinx-docs/source/help
cp -r docs sphinx-docs/source/help

PYTHONPATH=. sphinx-apidoc -e -f -o sphinx-docs/source riscemu riscemu/colors.py riscemu/__main__.py

rm sphinx-docs/source/modules.rst

cd sphinx-docs

make html

# xdg-open build/html/index.html