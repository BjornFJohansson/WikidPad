## Setuptools (pip) package for WikidPad (WikidPadMP)

Wikidpad (WP) is a personal wiki written in Python.
See the original repository for more information [here](https://github.com/WikidPad/WikidPad).

There are two important differences between this version and the original (see at the end of this page).

1. The original wikidpad is usually installed via a binary installer.
This version is installed as a setuptools or conda package.

2. A series of plugins (mec_plugins) are distributed along with WikidPadMP.
These are located in the WikidPad/user_extensions directory.
These files are named mecplugins_*.py and are useful for using Wikidpad as a dated notebook.
These files are not necessary and can be removed.

The requirements are (in requirements.txt) are:

	wxPython==4.1.1

Optional requirements are (in requirements.txt) are:

    dateparser>=1.1.5
    natsort>=8.2.0

These are needed for some of the mec_plugins

## Installation with pip

    pip install WikidPadMP

## Installation of optional requirements

    pip install -r requirements_optional.txt

## Installation with Anaconda

1. Install [Anaconda](https://www.anaconda.com/products/individual) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html).

2. Create a new conda environment with python 3.8 `conda create python=3.8 -n wp38`

3. Activate this environment `conda activate wp38`

4. Install wikidpad by `conda install -c bjornfjohansson wikidpadmp`

5. run from terminal by `~/anaconda3/envs/wp38/bin/wikidpad`

6. conda info

(bjorn39) bjorn@bjorn-ThinkPad-T450s:~$ conda info

     active environment : bjorn39
    active env location : /home/bjorn/anaconda3/envs/bjorn39
            shell level : 2
       user config file : /home/bjorn/.condarc
 populated config files : /home/bjorn/.condarc
          conda version : 4.9.2
    conda-build version : 3.20.5
         python version : 3.8.3.final.0
       virtual packages : __glibc=2.31=0
                          __unix=0=0
                          __archspec=1=x86_64
       base environment : /home/bjorn/anaconda3  (writable)
           channel URLs : https://conda.anaconda.org/conda-forge/linux-64
                          https://conda.anaconda.org/conda-forge/noarch
                          https://repo.anaconda.com/pkgs/main/linux-64
                          https://repo.anaconda.com/pkgs/main/noarch
                          https://repo.anaconda.com/pkgs/r/linux-64
                          https://repo.anaconda.com/pkgs/r/noarch
                          https://conda.anaconda.org/BjornFJohansson/linux-64
                          https://conda.anaconda.org/BjornFJohansson/noarch
          package cache : /home/bjorn/anaconda3/pkgs
                          /home/bjorn/.conda/pkgs
       envs directories : /home/bjorn/anaconda3/envs
                          /home/bjorn/.conda/envs
               platform : linux-64
             user-agent : conda/4.9.2 requests/2.25.1 CPython/3.8.3 Linux/5.4.0-64-generic linuxmint/20.1 glibc/2.31
                UID:GID : 1000:1000
             netrc file : None
           offline mode : False




active env location : /home/bjorn/anaconda3/envs/bjorn39


.desktop file for linux:

    #!/usr/bin/env xdg-open
    [Desktop Entry]
    Name=wikidpad
    Type=Application
    Exec=/home/bjorn/bin/wikidpad
    Terminal=false
    StartupNotify=true
    MimeType=
    Icon=/home/bjorn/Desktop/python_packages/WikidPad/WikidPad/Wikidpad_128x128x32.png
    Categories=Office;






## Conda packages

WikidPadMP can also be run from source in editable mode by downloading this repository:

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
