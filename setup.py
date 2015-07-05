#!/usr/bin/env python3
from distutils.core import setup
setup(
    name='choo',
    packages=['choo', 'choo.models', 'choo.apis'],
    py_modules=['choo.choo', 'choo.networks'],
    version='0.1.1',
    description='uniform interface for public transport APIs',
    author='Nils Martin Klünder',
    author_email='choo@nomoketo.de',
    url='https://github.com/NoMoKeTo/choo',
    install_requires=['requests'],
    license='Apache License 2.0',
    extras_require={
        'websockets': ['autobahn'],
        'msgpack': ['msgpack']
    },
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
