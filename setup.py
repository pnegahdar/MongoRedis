"""
mongoredis
-------------

Python redispy emulator for mongodb.
"""
from setuptools import setup

setup(
name='mongoredis',
    version='0.1',
    url='https://github.com/pnegahdar/mongoredis',
    license='See License',
    author='Parham Negahdar',
    author_email='pnegahdar@gmail.com',
    description='Redis emulator for mongodb',
    py_modules=['mongoredis'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'pymongo',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
