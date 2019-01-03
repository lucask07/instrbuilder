from __future__ import (absolute_import, division, print_function)
import glob
import versioneer

import setuptools

with open('requirements.txt') as f:
    requirements = f.read().split()

setuptools.setup(
    name='instrbuilder',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Lucas J. Koerner',
    author_email=koerner.lucas@stthomas.edu,
    license="MIT",
    url="https://lucask07.github.io/instrbuilder/build/html/",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
