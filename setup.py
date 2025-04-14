"""
@Author: Henve
@Date: 2025/4/14 13:47
@File: setup.py
@Description: 
"""
from setuptools import setup, find_packages

setup(
    name="password-manager",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        'cryptography',
        'tkinter',
    ],
    entry_points={
        'console_scripts': [
            'password-manager = password_manager.main:main',
        ],
    },
)
