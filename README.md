# A very dumb script to scrape manga sites

⚠ mangakakalot.com started using cloudflare and mangadex got hit with DMCA strike. So it as of now works for a few of the manga entries.

## What does it do?

This script is run manually to scrape new releases from different manga sites and compares them to the last read issues that are stored in the local [site_obj.json](site_obj.json)

## Usage:

```bash
$ python manga_checker -h
usage: manga_checker.py [-h] [-c] [-e] [-l] [-la] [-L] [-n]

Manga Checker

options:
  -h, --help            show this help message and exit
  -c, --count           Manga Count
  -e, --edit-code       Open in VSCode
  -l, --list            List Manga Sites
  -la, --list-alphabetically
                        List Manga Sites Alphabetically
  -L, --latest          List Latest Manga Chapters Urls
  -n, --new             Add Manga
```