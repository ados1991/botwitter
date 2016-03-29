#!/usr/bin/env python3

from distutils.core import setup
from glob import glob


setup(
    name='twspam',
    scripts=glob('scripts/*'),
    packages=[
        'twspam',
        'twspam_apps',
    ],
)
