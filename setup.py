from setuptools import setup

setup(
    name="searchads_api",
    description="Apple Searchads API non-official python library",
    version="1.7.11",
    url="https://github.com/phiture/searchads_api",
    author="Abdul Majeed Alkattan",
    author_email="alkattan@phiture.com",
    packages=["searchads_api"],
    keywords=["python", "searchads", "library"],
    install_requires=["requests", "pyjwt", "cryptography"],
    long_description="""

# About Phiture

http://phiture.com is a Berlin-based mobile growth consultancy working with the teams behind leading apps. Using the company’s industry-acclaimed Mobile Growth Stack as a strategic framework, Phiture team offers 4 key services: App Store Optimization, Apple Search Ads, User Retention services and Growth Consulting.


# Apple Searchads API Library in Python

In order to facilitate the usage of the Apple Search Ads API Phiture's Engineers 
have built a library in Python which allows users to manage campaigns, ad groups, 
keywords and creative sets. This library only requires intermediate Python skills 
and therefore makes it possible not only for Engineers but also for Data Analysts 
and Apple Search Ads Consultants to work with it.  
While the library is extensive it is not complete and users are encouraged to commit suggestions.

Read the docs on github.

# Example Usage:

Setup for v4 of the library

create a certs directory inside of your project folder, or create a different certs directory and specify it using the certificates_dir_path argument.

         api = SearchAdsAPI(2134535, "public.pem","private.key", 
         client_id="SEARCHADS.07875add-f6cd-4111-9c38-b84501d557c8",
         team_id="SEARCHADS.07879add-d6cd-4111-9c38-b84501d527c8",
         key_id="78a167b1-e423-4ab4-bcd1-8be75a4d7b7e", verbose=True)

### Campaign Methods

- Create a new campaign

         res = api.create_campaign(1433439534, ['AU'], "test", 1, 1, "EUR")

## Changelog

version 0.1.1 Added granularity level reports

version 0.7.1 fixed some issues with granularity

version 1.1.1 added support for the v4 of the Apple Search Ads API

version 1.2.1 refresh access_tokn only when needed

version 1.5.1 handles API error with Exception

version 1.5.3 fixed token update issue

version 1.6.1 added new product page, reporting, and Ad endpoints. Deprecated creatives endpoints

version 1.6.3 includes new bug fixes

version 1.7.1 added impression share reports and new find methods along product pages to match Searchads API version 4.7

version 1.7.6 fixed an issue with token update

version 1.7.7 fixed an issue update_campaign

version 1.7.8 updated the dependencies

version 1.7.9 always use the latest requests package

version 1.7.10 always use the latest cryptography package

version 1.7.11 added support for use cert and key as strings
    """,
)
