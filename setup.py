# -*- coding: utf-8 -*-

# Learn more: https://gitlab.pg.com/caggioni.m/rheology_toothpaste

from setuptools import setup, find_packages

readme='Python labrary for rheology data analysis'
licence='MIT'

setup(
    name='rheofit',
    version='0.1.2',
    description='Python library for rheology data analysis',
    long_description=readme,
    author='Marco Caggioni',
    author_email='marco.caggioni@gmail.com',
    url='https://github.com/rheopy/rheofit',
    license=licence,
    install_requires=['lmfit','xmltodict','emcee','corner','pybroom'],
    packages=['rheofit']
)
