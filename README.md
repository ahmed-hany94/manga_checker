# A very dumb script to scrape manga sites

## What does it do?

This script is run manually to scrape new releases from different manga sites and compares them to the last read issues that are stored in the local [site_obj.json](site_obj.json)

## site_obj.json

It's a json file stores the manga related _info_ that I need to keep track of what needs to be scraped. These _info_ are

```
"website": <website name>,
"manga_url": <url that has new manga releases>,
"name": <manga name>,
"url": <latest manga url>
```

## Usage

Run
python manga_checker

```
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Manga Update Found:             Kingdom         https://manganelo.com/chapter/kingdom/chapter_676
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
Nothing new (-_-)
```

Add new manga (interactive)

```
manga_checker -n
website: mangakakalot
manga_url: https://mangakakalot.com/read-aq1cl158504930275
name: Kings' Viking
url: https://mangakakalot.com/chapter/kings_viking/chapter_80
```

List manga alphabetically

```
manga_checker -l
```

Count manga

```
manga_checker -c
```
