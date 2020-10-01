## Setuptools (pip) package for WikidPad (WikidPadMP)

Wikidpad (WP) is a personal wiki written in Python. See the original repository for more information [here](https://github.com/WikidPad/WikidPad).

There are two important differences between this version and the original (see at the end of this page).

1. The original wikidpad is usually installed as a binary installer. This version is installed as a pip package.

    pip install WikidPadMP

2. plugins are distributed along with wikidpad. These are located in the WikidPad/user_extensions directory and can be removed.

We call these plugins "mecplugins" and they help us with biology and molecular biology work.

## Conda packages

https://anaconda.org/BjornFJohansson/wikidpadmp

conda install -c bjornfjohansson wikidpadmp

In a fresh conda environment, this WikidPadMP can also be run in editable mode by:

    conda install wxpython pillow matplotlib natsort scipy dateparser appdirs biopython prettytable networkx pyparsing gspread
    pip install --editable . --no-deps


# Where is what?

* [Main website](http://wikidpad.sourceforge.net/)
* [Downloads (Windows binary and source)](http://sourceforge.net/projects/wikidpad/files/?source=navbar)
* Installation hints for [Windows from source](http://trac.wikidpad2.webfactional.com/wiki/InstallWindows),
  [Linux](http://trac.wikidpad2.webfactional.com/wiki/InstallLinux),
  [MacOS](http://trac.wikidpad2.webfactional.com/wiki/InstallMacosxNew)
* [WikidPad's own wiki](http://trac.wikidpad2.webfactional.com/)
* [Source repository on Github](https://github.com/WikidPad/WikidPad/)


    with pydna in editable mode:

    conda install wxpython pillow matplotlib natsort scipy dateparser appdirs biopython prettytable networkx pyparsing gspread
