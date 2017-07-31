from setuptools import setup, find_packages

setup(
    name='digimat.saia',
    version='0.0.2',
    description='Digimat Saia EtherSBus (partial) client->server implementation',
    namespace_packages=['digimat'],
    author='Frederic Hess',
    author_email='fhess@splust.ch',
    url='http://www.digimat.ch',
    license='PSF',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'digimat.jobs',
        'setuptools'
    ],
    dependency_links=[
        ''
    ],
    zip_safe=False)
