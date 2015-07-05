#!/usr/bin/env python3
from distutils.core import setup
setup(
    name='choo',
    packages=['choo', 'choo.models', 'choo.apis'],
    py_modules=['choo.choo', 'choo.networks'],
    version='0.1.0',
    description='uniform interface for public transport APIs',
    author='Laura Klünder',
    author_email='choo@codingcatgirl.de',
    url='https://github.com/codingcatgirl/choo',
    install_requires=['requests'],
    scripts=['choo/choo'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Internet'],
)
