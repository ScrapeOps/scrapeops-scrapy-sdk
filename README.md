# ScrapeOps Scrapy SDK: Scrapy Extension For Spider Monitoring, Alerts and Scheduling.
The ScrapeOps Scrapy SDK is an extension for your Scrapy spiders that gives you all the scraping monitoring, statistics, alerting, scheduling and data validation you will need straight out of the box. 

Just enable it in your `settings.py` file and the SDK will automatically monitor your scrapers and send your logs to your scraping dashboard. When connected to a ScrapyD server, you can schedule and manage all your jobs from one easy to use interface.

**Full documentation can be found here:** [ScrapeOps Documentation](https://scrapeops.io/docs/intro)


![ScrapeOps Dashboard Demo](https://github.com/ScrapeOps/scrapeops-docs/blob/main/assets/scrapeops-hero-demo.jpg)


## :computer: Demo
[:link: ScrapeOps Dashboard Demo](https://scrapeops.io/app/login/demo)

## :star: Features
<details>
<summary>View features</summary>

- **Scrapy Job Stats & Visualisation**
  - :chart_with_upwards_trend: Individual Job Progress Stats
  - :bar_chart: Compare Jobs versus Historical Jobs
  - :100: Job Stats Tracked
    - :white_check_mark: Pages Scraped & Missed
    - :white_check_mark: Items Parsed & Missed
    - :white_check_mark: Item Field Coverage
    - :white_check_mark: Runtimes
    - :white_check_mark: Response Status Codes
    - :white_check_mark: Success Rates & Average Latencies
    - :white_check_mark: Errors & Warnings
    - :white_check_mark: Bandwidth

- **Health Checks & Alerts**
  - :male_detective: Custom Spider & Job Health Checks 
  - :package: Out of the Box Alerts - Slack (More coming soon!)
  - :bookmark_tabs: Daily Scraping Reports

 - **ScrapyD Cluster Management**
    - :link: Integrate With ScrapyD Servers
    - :alarm_clock: Schedule Periodic Jobs
    - :100: All Scrapyd JSON API Supported
    - :closed_lock_with_key: Secure Your ScrapyD with BasicAuth, HTTPS or Whitelisted IPs
 - **Proxy Monitoring (Coming Soon)**
    - :chart_with_upwards_trend: Monitor Your Proxy Account Usage
    - :chart_with_downwards_trend: Track Your Proxy Providers Performance
    - :bar_chart: Compare Proxy Performance Verus Other Providers

</details>

## :rocket: Getting Started
You can get the ScrapeOps monitoring suite up and running in **4 easy steps**.

#### #1 - Install the ScrapeOps SDK:

```
pip install scrapeops-scrapy
```

#### #2 - Get Your ScrapeOps API Key:
Create a [free ScrapeOps account here](https://scrapeops.io/app/register) and get your API key from the dashboard.

When you have your API key, open your Scrapy projects `settings.py` file and insert your API key into it. 

```python
SCRAPEOPS_API_KEY = 'YOUR_API_KEY'
```

#### #3 - Add in the ScrapeOps Extension:
In the `settings.py` file, add in the ScrapeOps extension, by simply adding it to the `EXTENSIONS` dictionary.

```python
EXTENSIONS = {
    'scrapeops_scrapy.extension.ScrapeOpsMonitor': 500, 
}
```

#### #4 - Enable the ScrapeOps Retry Middleware:
To get the most accurate stats, you need to add in the ScrapeOps retry middleware into the `DOWNLOADER_MIDDLEWARES` dictionary and disable the default Scrapy Retry middleware in your Scrapy project's `settings.py` file. 

You can do this by setting the default Scrapy RetryMiddleware to `None` and enabling the ScrapeOps retry middleware in it's place.

```python
DOWNLOADER_MIDDLEWARES = {
    'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
}
```

The retry middleware will operate the exactly as before, however, the ScrapeOps retry middleware will log every request, response and exception your spiders generate. 

#### #5 - (Optional) Exclude Settings From Being Logged By ScrapeOps SDK:
By default the ScrapeOps SDK will log the settings used for each particular scrape so you can keep track of the settings used. However, to ensure it doesn't record sensitive information like API keys it won't log any settings that contain the following substrings:

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

#### Done!
That's all. From here, the ScrapeOps SDK will automatically monitor and collect statistics from your scraping jobs and display them in your [ScrapeOps dashboard](https://scrapeops.io/app/dashboard). 
