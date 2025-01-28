from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="searchads_api",
    description="Apple Searchads API non-official python library",
    version="1.7.20",
    url="https://github.com/phiture/searchads_api",
    author="Abdul Majeed Alkattan",
    author_email="alkattan@phiture.com",
    packages=["searchads_api"],
    keywords=["python", "searchads", "library", "apple"],
    install_requires=["requests", "pyjwt", "cryptography"],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
