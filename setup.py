from setuptools import setup
from setuptools import find_packages


VERSION = '0.1.0'
DESCRIPTION = 'Scrapeops Scrapy SDK (MVP)'

setup(name='scrapeops_scrapy',
      description=DESCRIPTION,
      version=VERSION,
      packages=find_packages(),
      install_requires=[
          "tld==0.12.4",
          "requests==2.24.0",
          "json5==0.9.5",
          "urllib3==1.25.10",
          "uuid==1.30",
          ]
      )