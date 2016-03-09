from pyrocopy import pyrocopy
from setuptools import setup, find_packages

setup(
    name='pyrocopy',

    version=pyrocopy.__version_str__,

    description='A suite of robust file copying utilities for Python.',
	long_description="""pyrocopy is a suite of advanced file utility functions for efficiently copying all or part of a directory tree. It can be used as a module in your own application or run as a standalone command line tool.

Main Features
-------------
-  Mirror Mode
-  Sync Mode (bi-directional copy)
-  Regular expression based filename and directory matching
-  Configurable maximum tree depth traversal
-  Detailed operation statistics

For complete documentation please visit the project page on `GitHub <https://github.com/caskater4/pyrocopy>`_.""",

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