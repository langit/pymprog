.. A simple tutorial by Yingjie Lan, May 2009.

###################
Setup PyMathProg
###################

Setup Latest Version
========================

Setting up the latest PyMathProg can't be easier, 
just open a terminal and issue this command:

.. prompt:: bash

   python -m pip install pymprog

That's all you need to do and in just a few
seconds you are all set! It already takes care
of installing swiglpk to use GLPK within python.
Note that on Windows you might need the privilage 
of an administrator to install it 
(start menu --> in the search box type in 'cmd' 
--> right click on the dos icon --> click 'run as admininstrator'),
and on Linux or Mac OSX, you may need to use sudo
to acquire super user privilage to install something:

.. prompt:: bash

   sudo python -m pip install pymprog

In case pip is not installed on your system,
you may try this(use sudo if necessary, or on 
windows try to run as administrator):

.. prompt:: bash

   python -m easy_install pip

It is the same simple way to setup PyMathProg
on all operating systems
(be it Mac OSX, Linux, or Windows) and for
all recent Python 2 and 3 versions. 
Unless you are curious about other ways to setup 
PyMathProg, you can pretty much skip the rest of 
this document and proceed to the next chapter.

Alternative ways
================

You can also use PyMathProg by just putting the single 
pure python source file pymprog.py in the same folder 
as your python file that imports pymprog.
Go to `SourceForge PyMathProg Project
<https://sourceforge.net/projects/pymprog/>`_
and download the compressed source distribution file,
then decompress it into your current folder.
All the documentation files also come along with the
python module file, ready for offline browsing. 

Before you can use PyMathProg, however, you need to 
have swiglpk installed first:

.. prompt:: bash

   pip install swiglpk>=1.3.3

On Linux or Mac OSX, you may need to use sudo.
When the source file pymprog.py is available in your
current working directory, you can enter an interactive
session like this in a terminal:

.. prompt:: bash

   python -i pymprog.py

This way a python session will start with pymprog 
fully imported, so that you can start modelling
right away.

Finally, if you have all the sources decompressed
into a folder, you may also install PyMathProg
from that folder(which contains the file pymprog.py).  

.. prompt:: bash

   cd /path/to/decompressed/pymprog/
   pip install . 

On Linux or Mac OSX, you may need to use sudo.
Without pip on your system, you may try this and 
see if you are lucky enough(it may not work 
sometimes):

.. prompt:: bash

   cd /path/to/decompressed/pymprog/
   python setup.py

Again, on Linux or Mac OSX, you may need to use sudo.


Setup OLD versions
==================

Newer versions are much easier to setup, and more useful.
Upgrading to the newest version is highly recomended. 
Setup instructions for new versions(>0.6.0) are provided
in the beginning of this chapter.
 
If you insist on using old versions(<=0.6.0), 
or if you rather like the challenge involved,
here are some instructions on how to setup your
environment to run old versions of PyMathProg. 
Please choose your platform:

#. :ref:`wind-setup`.
#. :ref:`linux-setup`.
#. :ref:`mac-setup`.

.. _wind-setup:

Setup on Windows
-------------------

The easy way:
^^^^^^^^^^^^^

#. Setup Python 2.5.4. 

#. Install GLPK: a setup program can be downloaded
   `here <http://gnuwin32.sourceforge.net/packages/glpk.htm>`_ 
   and make sure your PATH enviroment variable
   contains the path to the glpk.dll file
   (by default in english language, it is in folder
   "C:\\Program Files\\GnuWin32\\bin").

#. Download dist#.#.zip (where #.# is the version)
   and unzip it, you will find two windows installer,
   and a zip file containing the source files.
   Run both installers. Unzip the source files and 
   you can now play with the examples there. 

The hard way:
^^^^^^^^^^^^^

#. If you would like to complile pyglpk yourself: 
   Setup Python 2.5.x (2.6.x, 2.7.x also works) 
   and MinGW 5.1.6 (MinGW has gcc compiler -- 
   the minimal installation should work. 
   For more information, please refer to the appendix.

#. Install GLPK: a setup program can be downloaded
   `here <http://gnuwin32.sourceforge.net/packages/glpk.htm>`_ and when you
   install, make sure you install it in the "C:\\Program Files\\GnuWin32" 
   folder. If you installed it somewhere else, you have to modify the 'setup.py' 
   file to change the hardcoded installation directory of GLPK.
   For example, in the help forum of pymprog on sourceforge, Sano 
   provided a way to install on Windows 64 bit, with some 
   clever changes to the 'setup.py' file. Instead of::

      libdirs = ['C:\\Program Files\\GnuWin32\\bin']
      incdirs = ['C:\\Program Files\\GnuWin32\\include'] 

   it needs to be::

      libdirs = ['C:\\Program Files (x86)\\GnuWin32\\bin'] 
      incdirs = ['C:\\Program Files (x86)\\GnuWin32\\include'] 

#. Make sure your %PATH% environment variable
   contains "C:\\Python25;C:\\MinGW\\bin;C:\\Program Files\\GnuWin32\\bin", 
   assuming you have installed them that way (the default).
#. Install PyGLPK (skip this step if pymprog version >= 0.3.0): 
   unzip the source code of pyglpk (please goto the download
   section of `pymprog <https://sourceforge.net/projects/pymprog/>`_
   project page at source forge -- other sources might not compile on windows),
   go to the top folder that contains the setup.py file, issue this command::

      python setup.py build --compiler=mingw32 install

   to have it installed.
#. Also download the source code for pymprog, unzip it and open a command 
   window (click Start->Run->type in 'cmd') 
   and change to the unzipped folder, run::

      python setup.py build --compiler=mingw32 install

   Note: the compiler from the freely available 
   `Microsoft Visual C++ 2008 Express Edition 
   <http://www.microsoft.com/express/download/#webInstall>`_
   is not recommended.

   If you would like to build a binary distribution, issue this command::

      python setup.py build --compiler=mingw32 bdist_wininst

   Then the distribution files (binary installers) 
   are stored in the 'dist' folder

.. _linux-setup:

Setup on Linux
-------------------

#. Setup Python 2.4 or later.
#. Install GLPK. For more information, visit
   `GLPK homepage <http://www.gnu.org/software/glpk/>`_.
#. Install PyGLPK (skip this step if pymprog version >= 0.3.0): 
   unzip the source code of pyglpk (please goto the download
   section of `pymprog <https://sourceforge.net/projects/pymprog/>`_
   project page at source forge -- other sources might not compile on windows),
   go to the top folder that contains the setup.py file, issue this command::
     
      python setup.py install

   to have it installed.
#. Also download the source code for pymprog, unzip it and start playing with
   the examples. If you wish, you can also install it, by running::

      ~/pymprog$ python setup.py install

   once you have changed to the folder you have unzipped pymprog into.

.. _mac-setup:


Setup on Mac OSX
-------------------

#. Setup Python 2.4 or later (Mac has that by default, so you should need to do nothing).
#. Setup glpk. Make sure you have the right version of xcode and MacPort for your 
   version of Mac OSX (download the right dmg files, and follow the installation steps), 
   then type this in a terminal::

      sudo port install glpk

   and that should install glpk onto your system.
#. Download pymprog0.3.1 or later, unzip and change to the base folder::

      sudo python setup.py install

   and that's it.
