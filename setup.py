from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='openvcloud',
    version='3.0',
    description='openvcloud library',
    long_description=long_description,
    url='https://docs.greenitglobe.com/openvcloud/openvcloud',
    author='Jo De Boeck',
    author_email='deboeckj@gig.tech',
    packages=find_packages(),
    install_requires=['Jinja2', 'mongolock', 'pycapnp'],
)
