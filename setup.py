#from distutils.core import setup
from setuptools import setup

setup(name='amplet2-collector',
        version='1.0',
        description='AMP Time Series Collector',
        author='Brendon Jones',
        author_email='brendonj@waikato.ac.nz',
        url='https://amp.wand.net.nz',
        packages=['amplet2_collector','amplet2_collector.tests'],
        scripts=['bin/amplet2-collector'],
        install_requires=['pika', 'influxdb','ampsave'],
     )
