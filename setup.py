# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='HSRLCA',
    version='0.1.9',
    description='A package for life cycle assessment modeling of Chinese high-speed rail (HSR) development in continental East and Southeast Asia.',
    long_description=readme,
    author='Cory Combs',
    author_email='cory.j.combs@outlook.com',
    url='https://github.com/coryjcombs/HSRLCA',
    license='LICENSE.txt',
    packages=find_packages(exclude=('tests', 'docs', 'examples'))
)