from setuptools import setup

setup(
        name="timesheet",
        version="1.0",
        py_module=["timesheet"],
        install_requires=[
            "click",
            "sqlalchemy",
            "XlsxWriter"
            ],
        entry_points='''
            [console_scripts]
            ts=cli:cli
        '''
        )
