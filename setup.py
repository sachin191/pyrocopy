from pyrocopy import pyrocopy
from setuptools import setup, find_packages

setup(
    name='pyrocopy',

    version=pyrocopy.__version_str__,

    description='Robust file copying utilties for Python.',

    url='https://github.com/caskater4/pyrocopy',

    author='Jean-Philippe Steinmetz',

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
        'Topic :: Software Development :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
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