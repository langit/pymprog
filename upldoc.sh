#!/bin/bash
cd docs
make clean
make html
cd _build/html
scp -r . lanyjie@web.sourceforge.net:/home/project-web/pymprog/htdocs
