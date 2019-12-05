#!/bin/bash 

# source ./virtaulenv.bash
python setup.py build
python setup.py install

py-trees-demo-tree-pilar -i

#py-trees-demo-testemphasis -r

