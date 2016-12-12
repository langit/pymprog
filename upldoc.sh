#!/bin/bash
cd docs
make html
cd _build/html
scp -vr . lanyjie@web.sourceforge.net:/home/project-web/pymprog/htdocs
