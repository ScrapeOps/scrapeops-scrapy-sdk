# ScrapeOps Scrapy SDK (MVP)
Most up to date version of the ScrapeOps Scrapy SDK. 

To install you need to install the package by going into the root folder (contains ReadMe) and installing it:

```
pip install git+https://github.com/ScrapeOps/scrapeops-scrapy-sdk
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
To get the most accurate stats, you need to add in the ScrapeOps retry middleware into the `DOWNLOADER_MIDDLEWARES` dictionary and disable the default Scrapy Retry middleware:

```python
DOWNLOADER_MIDDLEWARES = {
    'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
}
```

#### #3 Set Your ScrapeOps API Key:
Set your ScrapeOps API key so your logs can be linked to your account:

```python
SCRAPEOPS_API_KEY = 'YOUR_API_KEY'
```


#### #4 Exclude Settings From Being Logged By ScrapeOps SDK:
The ScrapeOps SDK will log the settings used for each particular scrape. It won't log any settings that contain the following substrings:

- `API_KEY`
- `APIKEY`
- `SECRET_KEY`
- `SECRETKEY`

However, it can still log other settings that don't match these patterns. You can specify which settings not to log by adding the setting to the `SCRAPEOPS_SETTINGS_EXCLUSION_LIST`. 

```python
SCRAPEOPS_SETTINGS_EXCLUSION_LIST = [
    'NAME_OF_SETTING_NOT_TO_LOG'
]
```










