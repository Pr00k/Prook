#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="ProokSuitePro",
    version="2.0.0",
    description="Professional Modding & Analysis Tool",
    author="ProokSuite",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.5.0",
        "psutil>=5.9.0",
        "pycryptodome>=3.19.0",
    ],
    entry_points={
        "console_scripts": [
            "prooksuite=app.main:main",
        ],
    },
)
