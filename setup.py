
# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

# dephell deps convert --from=pyproject.toml --to=setup.py

VERSION = '0.3.0'

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme = ''

setup(
    long_description=readme,
    name='rocksdbdict',
    version=VERSION,
    python_requires='==3.*,>=3.7.0',
    author='Adam Marples',
    author_email='adammarples@gmail.com',
    license='MIT',
    packages=[],
    package_dir={"": "."},
    package_data={},
    install_requires=['python-rocksdb==0.*,>=0.7.0'],
    extras_require={"dev": ["dephell==0.*,>=0.8.3", "pytest==6.*,>=6.1.2"]},
    download_url=f'https://github.com/adammarples/rocksdbdict/archive/{VERSION}.tar.gz',
)
