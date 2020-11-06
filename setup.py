
# -*- coding: utf-8 -*-

from os import path

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


VERSION = '0.6.0'

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    readme = f.read()


setup(
    long_description=readme,
    long_description_content_type='text/markdown',
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
    url='https://github.com/adammarples/rocksdbdict',
)
