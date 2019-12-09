from setuptools import setup
import setuptools

setup(
    name='searchads_api',
    description='Apple Searchads API non-official python library',
    version='0.1',
    url='https://github.com/phiture/searchads_api',
    author='Abdul Majeed Alkattan',
    author_email='alkattan@phiture.com',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7.4",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=['python','searchads','library'],
    install_requires=['requests>=2.22.0']
    )