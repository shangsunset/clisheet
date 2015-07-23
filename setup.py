from setuptools import setup
import os
import re
import sys


setup(
    name='clisheet',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.0.3',

    description='A command line tool for time tracking',

    # The project's main homepage.
    url='https://github.com/shangsunset/clisheet',
    download_url = 'https://github.com/shangsunset/clisheet/tarball/0.1',

    # Author details
    author='Yeshen Shang',
    author_email='shangsunset@gmail.com',

    # Choose your license
    #license='MIT',


    # What does your project relate to?
    keywords='time tracking cli',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['timesheet'],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
            'click',
            'sqlalchemy',
            'XlsxWriter'
            ],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    # extras_require={
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={
    #     'sample': ['package_data.dat'],
    # },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    zip_safe=False,
    entry_points='''
        [console_scripts]
        sheet=timesheet.main:cli
    '''
)
