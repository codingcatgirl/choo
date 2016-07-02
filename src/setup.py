#!/usr/bin/env python3
import importlib
import os

from setuptools import find_packages, setup

os.environ['CHOO_NOIMPORT'] = '1'

setup(
    name='choo',
    packages=find_packages(),
    version=importlib.import_module('choo').__version__,
    description='uniform interface for public transport APIs',
    author='Laura Klünder',
    author_email='choo@codingcatgirl.de',
    url='https://github.com/codingcatgirl/choo',
    install_requires=['requests', 'defusedxml'],
    license='Apache License 2.0',
    scripts=['choo/choo-cli', 'choo/choo-server'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Internet'],
    include_package_data=True
)
