#!/bin/bash
ZIPF=`pwd`/$1-$(date +"%H%M%S").zip
git archive --format zip --output $ZIPF master
cd docs
make clean
make html
cd _build
zip -r $ZIPF html
echo $ZIPF
#scp $ZIPF lanyjie@frs.sourceforge.net:/home/frs/project/p/py/pymprog/pymprog-1.0/pymprog-1.1.1.zip
