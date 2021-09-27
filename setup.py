from setuptools import setup
import setuptools

setup(
    name='searchads_api',
    description='Apple Searchads API non-official python library',
    version='1.5.1',
    url='https://github.com/phiture/searchads_api',
    author='Abdul Majeed Alkattan',
    author_email='alkattan@phiture.com',
    packages=["searchads_api"], 
    keywords=['python','searchads','library'],
    install_requires=['requests>=2.22.0', 'PyJWT==2.1.0', 'cryptography==3.4.4'],
    long_description="""

# About Phiture

_[Phiture](http://phiture.com) is a Berlin-based mobile growth consultancy working with the teams behind leading apps. Using the company’s industry-acclaimed Mobile Growth Stack as a strategic framework, Phiture team offers 4 key services: App Store Optimization, Apple Search Ads, User Retention services and Growth Consulting._

### Apple Searchads API Library in Python

In order to facilitate the usage of the Apple Search Ads API Phiture's Engineers have built a library in Python which allows users to manage campaigns, ad groups, keywords and creative sets. This library only requires intermediate Python skills and therefore makes it possible not only for Engineers but also for Data Analysts and Apple Search Ads Consultants to work with it.  While the library is extensive it is not complete and users are encouraged to commit suggestions.

Read the docs on github.

Backlog
Added granularity level reports
version 0.7 fixed some issues with granularity
version 1.1 added support for the v4 of the Apple Search Ads API
version 1.2 refresh access_tokn only when needed
version 1.5 handles API error with Exception
    """,
    
    )