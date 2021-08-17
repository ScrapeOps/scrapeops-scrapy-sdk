# ScrapeOps Scrapy SDK (MVP)
Most up to date version of the ScrapeOps Scrapy SDK. 

To install you need to install the package by going into the root folder (contains ReadMe) and installing it:

```
pip install scrapeops_scrapy
```

## Setup the SDK in Scrapy Project

In the `settings.py` file withing your Scrapy Project, you need to do the following steps:

#### #1 Add in the ScrapeOps extension:

```python
EXTENSIONS = {
    'scrapeops_scrapy.extension.ScrapeOpsMonitor': 500, 
}
```

#### #2 Enable the ScrapeOps stats middleware:
Add in the ScrapeOps stats middleware into the `DOWNLOADER_MIDDLEWARES` dictionary:

```python
DOWNLOADER_MIDDLEWARES = {
    'scrapeops.middleware.stats.ScrapeOpsStats': 840,
}
```

#### #3 Set Your ScrapeOps API Key:
Set your ScrapeOps API key so your logs can be linked to your account:

```python
SCRAPEOPS_API_KEY = 'YOUR_API_KEY'
```










