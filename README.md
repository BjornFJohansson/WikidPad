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

The requirements are python 3.8 and (in requirements.txt):

	wxPython==4.1.1

Optional requirements are (in requirements.txt) are:

    dateparser>=1.1.5
    natsort>=8.2.0

These are needed for some of the mec_plugins

## Installation with pip

    pip install WikidPadMP

## Installation of optional requirements

    pip install -r requirements_optional.txt

## Installation with Mambaforge

1. Install [Mambaforge](https://mamba.readthedocs.io/en/latest/installation.html).

2. Create a new conda environment with python 3.8 `mamba create python=3.8 -n wp38`

3. Activate this environment `conda activate wp38`

4. Install wikidpad by `conda install -c bjornfjohansson wikidpadmp`

5. run from terminal by `~/anaconda3/envs/wp38/bin/wikidpad`

```
11:17 $ mamba info

     active environment : wp38
    active env location : /home/bjorn/anaconda3/envs/wp38
            shell level : 3
       user config file : /home/bjorn/.condarc
 populated config files : /home/bjorn/.condarc
          conda version : 22.9.0
    conda-build version : 3.23.1
         python version : 3.9.15.final.0
       virtual packages : __linux=5.15.0=0
                          __glibc=2.31=0
                          __unix=0=0
                          __archspec=1=x86_64
       base environment : /home/bjorn/anaconda3  (writable)
      conda av data dir : /home/bjorn/anaconda3/etc/conda
  conda av metadata url : None
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
             user-agent : conda/22.9.0 requests/2.28.1 CPython/3.9.15 Linux/5.15.0-56-generic linuxmint/20.3 glibc/2.31
                UID:GID : 1000:1000
             netrc file : None
           offline mode : False

My .desktop file for linux:

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


```
# Where is what?

* [Main website](http://wikidpad.sourceforge.net/)
* [Downloads (Windows binary and source)](http://sourceforge.net/projects/wikidpad/files/?source=navbar)
* Installation hints for [Windows from source](http://trac.wikidpad2.webfactional.com/wiki/InstallWindows),
  [Linux](http://trac.wikidpad2.webfactional.com/wiki/InstallLinux),
  [MacOS](http://trac.wikidpad2.webfactional.com/wiki/InstallMacosxNew)
* [WikidPad's own wiki](http://trac.wikidpad2.webfactional.com/)
* [Source repository on Github](https://github.com/WikidPad/WikidPad/)
