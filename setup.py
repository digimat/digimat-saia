from setuptools import setup, find_packages

from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='digimat.saia',
    version='0.0.92',
    description='SAIA Burgess PCD EtherSBus Client+Server communication module',
    long_description=long_description,
    namespace_packages=['digimat'],
    author='Frederic Hess',
    author_email='fhess@st-sa.ch',
    url='http://www.digimat.ch',
    license='PSF',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'future',
        'netifaces',
        'ipaddress',
        'digimat.jobs',
        'setuptools'
    ],
    dependency_links=[
        ''
    ],
    zip_safe=False)
