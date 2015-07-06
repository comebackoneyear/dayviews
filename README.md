dayviews
========

A Dayviews downloader and  browser.
Downloads both images and JSON-files with descriptions and comments.

###Requirements
* Python 2.7
* `screen` or other screen multiplexer (Optional)

###Usage
Edit the download.py to set USERNAME and PASSWORD.
Start the downloader with `python downloader.py`.
Once it hits a rate limit from the API it will go to sleep so if you have a lot of images, start it in a `screen` process

###Notes
* Resuming is only partially supported.
* The webserver viewer is not completed and still needs a lot of work.
* Error handling is basicly non-existent.
