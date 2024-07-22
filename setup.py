from setuptools import setup, find_packages


VERSION = '0.5.6'
DESCRIPTION = 'Scrapeops Scrapy SDK, is a monitoring tool for your Scrapy spiders.'

setup(name='scrapeops_scrapy',
      description=DESCRIPTION,
      long_description=DESCRIPTION,
      author="ScrapeOps",
      author_email="info@scrapeops.io",
      version=VERSION,
      license="BSD",
      url="https://github.com/ScrapeOps/scrapeops-scrapy-sdk",
      packages=find_packages(),
      install_requires=[
          "tld>=0.13",
          "requests>=2.32.0",
          "json5>=0.9.13",
          # The latest version of requests (2.29.0) does not support urllib3 2.0.0 #6432 - https://github.com/psf/requests/issues/6432
          "urllib3>=1.26.14", 
          "itemadapter>=0.8.0",
          ],
      classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
      ],
      python_requires=">=3.8",
      )