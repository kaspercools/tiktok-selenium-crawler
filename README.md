# tiktok-selenium-crawler

This quick and rather dirty script, including others, was written to help with autamatically scraping data from TikTok as part of my Master's thesis. Further details can be found at [github.com/kaspercools/tiktok-offensive-language-classifier](https://github.com/kaspercools/tiktok-offensive-language-classifier)

The `data-reader.py`file maps the results to individual files for further processing. The original data was obtained using our [Bright Data Collector script](https://github.com/kaspercools/bright-data-collector). Subsequently, the crawler.py file processes these and adds comments gathered from TikTok to these data files.
These data-files were later used to populate our MongoDB collections.

### Developers discretion is advised
Note that this script may not be all that well written or conform to Python conventions. We quickly wrote this code to meet our needs for automatically collecting data. This script was one of a few that contributed in continuous and automated collection and processing all the information hence why we start off by writing an endless while loop.

## License

All source code is made available under a MIT license. You can freely use and modify the code, without warranty, so long as you provide attribution to the authors. See LICENSE for the full license text.
