mkdoc
=====

A simple static wiki generator. Uses markdown files

Installation
------------

### Requirements

- Python 2.6 +
- Jinja2


To install Jinja2, please run one of the following commands as root

    easy_install Jinja2
    pip install Jinja2

Now clone this repository

    git clone https://github.com/niahoo/mkdoc.git
    cd mkdoc

Then add in your path a symlink to mkdoc.py

    ln src/mkdoc.py /home/$USER/bin/mkdoc

Using
-----

mkdoc command must now be in your path.

Let say you have your makrdown formatted files in /home/wiki/md-src,
as we actually support only this name for the sources directory.

Go into /home/wiki, launch mkdoc:

    cd /home/wiki
    mkdoc

Now you should have a directory containing the generated HTML files:
/home/wiki/www
