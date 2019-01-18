from __future__ import (absolute_import, division, print_function)
import glob
import setuptools
import re

def extract_requirements(filename):
    dependency_links = []
    VCS_PREFIXES = ('git+', 'hg+', 'bzr+', 'svn+')
    requirements = []

    with open(filename) as requirements_file:
        lines = requirements_file.read().splitlines()
        for package in lines:
            if not package or package.startswith('#'):
                continue
            if any(package.startswith(prefix) for prefix in VCS_PREFIXES):
                dependency_links.append(package)
                if re.search('#egg=(.*)', package):
                    package = package.split('=')[1]
                else:
                    raise ValueError('Please enter "#egg=package_name" at the'
                                     'end of the url.')
            package = package.replace('-','==')  
            requirements.append(package)

    return requirements, dependency_links


required, dependency_links = extract_requirements('requirements.txt')
print('Setup required: ')
print(required)
print('Dependency links: ')
print(dependency_links)


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='instrbuilder',
    version="0.1.4",
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
    install_requires=required,
    dependency_links=dependency_links,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
