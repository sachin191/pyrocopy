import pypandoc
from pyrocopy import pyrocopy
from setuptools import setup, find_packages

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name='pyrocopy',

    version=pyrocopy.__version_str__,

    description='A suite of robust file copying utilities for Python.',
	long_description=long_description,

    url='https://github.com/caskater4/pyrocopy',

    author='Jean-Philippe Steinmetz',
	author_email='caskater47@gmail.com',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
    ],

    keywords='file utilities admin filesystem copy move mirror sync',

    packages=find_packages(exclude=['tests']),

    install_requires=[],
    entry_points={
        'console_scripts': [
            'pyrocopy=pyrocopy:main',
        ],
    },
)