from __future__ import (absolute_import, division, print_function)
import glob
import setuptools

with open('requirements.txt') as f:
    requirements = f.read().split()

setuptools.setup(
    name='instrbuilder',
    version="0.0.1",
    author='Lucas J. Koerner',
    author_email="koerner.lucas@stthomas.edu",
    description="electrical instrument control",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://lucask07.github.io/instrbuilder/build/html/",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
