from setuptools import setup

setup(
        name="timesheet",
        version="1.0",
        py_module=["timesheet"],
        install_requires=[
            "click",
            "sqlalchemy",
            ],
        entry_points='''
            [console_scripts]
            ts=cli:main
        '''
        )
