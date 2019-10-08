# -*- coding: utf-8 -*-

# Learn more: https://gitlab.pg.com/caggioni.m/rheology_toothpaste

from setuptools import setup, find_packages

readme='Python labrary for rheology data analysis'
licence='No licence'

setup(
    name='rheology',
    version='0.1.0',
    description='Python labrary for rheology data analysis',
    long_description=readme,
    author='Marco Caggioni',
    author_email='caggioni.m@pg.com',
    url='https://gitlab.pg.com/caggioni.m/rheology_python',
    license=license,
    install_requires=['lmfit','xmltodict'],
    packages=['rheology']
)
