try:
        from setuptools import setup
except ImportError:
        from distutils.core import setup

#This setup file is provided by Yingjie Lan <ylan@pku.edu.cn>
#to faciliate the installation of PyMathProg.

with open('README.rst') as readme:
    ld = readme.read()

setup(name = 'pymprog',
      version = '1.1.1',
      description = 'An easy and flexible mathematical programming environment for Python',
      long_description = ld,
      author = 'Yingjie Lan',
      author_email = 'ylan@pku.edu.cn',
      url = 'http://pymprog.sourceforge.net/',
      keywords = "glpk math optimization LP MIP", 
      license = 'GPL',
      classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Education',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Programming Language :: Python',
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
    #'Operating System :: Platform Independent',
    'Topic :: Scientific/Engineering :: Mathematics'],
      py_modules=['pymprog'], #to include ./pymprog.py
      install_requires=['swiglpk >= 1.3.3'], # install it automatically?
)

