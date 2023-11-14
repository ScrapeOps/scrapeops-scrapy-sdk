from setuptools import setup, find_packages


VERSION = '0.5.4'
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
          "requests>=2.31.0",
          "json5>=0.9.13",
          "urllib3>=2.1",
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