#!/usr/bin/env python
"""setup.py"""

import setuptools

setuptools.setup(
    name='lslocks',
    author='Benjamin Staffin',
    author_email='benley@gmail.com',
    scripts=['lslocks.py'],
    install_requires=['psutil']
)
