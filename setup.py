from __future__ import (absolute_import, division, print_function)
import glob
import setuptools

with open('requirements.txt') as f:
    requirements = f.read().split()

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='instrbuilder',
    version="0.0.3",
    author='Lucas J. Koerner',
    author_email="koerner.lucas@stthomas.edu",
    description="electrical instrument control",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://lucask07.github.io/instrbuilder/build/html/",
    packages=setuptools.find_packages(),
    package_data={'instrbuilder': ['instrbuilder/example_yaml/config.yaml',
        'instruments/*']},
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
