import requests
from bs4 import BeautifulSoup
import json
import argparse
import sys
import numbers
import os

# TODO: This is breaks if I change the files position
if sys.platform == "win32":
    JSON_FILE = "G:\\Baka\\Repos\\my_projects\\manga_checker\\site_obj.json"
else:
    JSON_FILE = "/mnt/g/Baka/Repos/my_projects/manga_checker/site_obj.json"


def scrape_managakalot(text, url, name):
    try:
        soup = BeautifulSoup(text, "lxml")
        all_chapter_elements = soup.find_all("div", {"class": "row"})
        last_entry_url = all_chapter_elements[1].a["href"]
        if url == last_entry_url:
            print("Nothing new (-_-)")
            return url
        else:
            print("Manga Update Found: \t\t" + name + "\t\t" + last_entry_url)
            return last_entry_url
    except IndexError as e:
        print(name + " has a problem")
        print(e)
    except KeyboardInterrupt:
        exit(0)


def scrape_manganelo(text, url, name):
    try:
        soup = BeautifulSoup(text, "lxml")
        all_chapter_elements = soup.find_all("li", {"class": "a-h"})
        last_entry_url = all_chapter_elements[0].a["href"]
        if url == last_entry_url:
            print("Nothing new (-_-)")
            return url
        else:
            print("Manga Update Found: \t\t" + name + "\t\t" + last_entry_url)
            return last_entry_url
    except IndexError as e:
        print(name + " has a problem")
        print(e)
    except KeyboardInterrupt:
        exit(0)


def scrape_readheroacademia(text, url, name):
    try:
        soup = BeautifulSoup(text, "lxml")
        last_entry_url = soup.find_all("td")[0].a["href"]
        if url == last_entry_url:
            print("Nothing new (-_-)")
            return url
        else:
            r = requests.get(last_entry_url)
            if "Countdown" in r.text:
                print("Nothing new (-_-)")
                return url
            else:
                print("Manga Update Found: \t\t" + name + "\t\t" + last_entry_url)
                return last_entry_url
    except IndexError as e:
        print(name + " has a problem")
        print(e)
    except KeyboardInterrupt:
        exit(0)


def scrape_read_boruto(text, url, name):
    try:
        soup = BeautifulSoup(text, "lxml")
        last_entry_url = soup.find_all("li", {"class": "row"})[0].div.a["href"]

        if url == last_entry_url:
            print("Nothing new (-_-)")
            return url
        else:
            print("Manga Update Found: \t\t" + name + "\t\t" + last_entry_url)
            return last_entry_url
    except IndexError as e:
        print(name + " has a problem")
        print(e)
    except KeyboardInterrupt:
        exit(0)


def scrape_manhuascan(text, url, name):
    try:
        soup = BeautifulSoup(text, "lxml")
        last_entry_url = (
            "https://manhuascan.com/"
            + soup.find_all("span", {"class": "title"})[0].a["href"]
        )

        if url == last_entry_url:
            print("Nothing new (-_-)")
            return url
        else:
            print("Manga Update Found: \t\t" + name + "\t\t" + last_entry_url)
            return last_entry_url
    except IndexError as e:
        print(name + " has a problem")
        print(e)
    except KeyboardInterrupt:
        exit(0)


def check_for_updates(file):
    data = json.load(file)
    # TODO: Probably a design pattern is needed here

    for _, el in enumerate(data["sites"]):
        website = el["website"]
        manga_url = el["manga_url"]
        url = el["url"]
        name = el["name"]

        try:
            r = requests.get(manga_url)
            text = r.text

            if r.ok:
                if website == "mangakakalot":
                    el["url"] = scrape_managakalot(text, url, name)
                elif website == "manganelo":
                    el["url"] = scrape_manganelo(text, url, name)
                elif website == "readheroacademia":
                    el["url"] = scrape_readheroacademia(text, url, name)
                elif website == "read-boruto":
                    el["url"] = scrape_read_boruto(text, url, name)
                elif website == "manhuascan":
                    el["url"] = scrape_manhuascan(text, url, name)
                else:
                    print("Website not supported")
                    exit(0)

        except requests.exceptions.RequestException as e:
            print(e)
        except KeyboardInterrupt:
            exit(0)
    return data


def add_manga():
    try:
        with open(JSON_FILE) as f:
            data = json.load(f)
            w = input("website: ")
            m = input("manga_url: ")
            n = input("name: ")
            u = input("url: ")
            if w and m and n and u:
                data["sites"].append(
                    {"website": w, "manga_url": m, "name": n, "url": u}
                )
                print("Saved")
            else:
                print("Error, not saved!!")
            f.close()
    except KeyboardInterrupt:
        exit(0)

    return data


def update_json(data):
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=4)
        f.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--new_manga", help="add new manga", action="store_true")
    parser.add_argument("-c", "--count", help="how many manga", action="store_true")
    parser.add_argument("-l", "--list", help="list manga_sites", action="store_true")
    args = parser.parse_args()

    if args.new_manga:
        data = add_manga()
        update_json(data)
        exit(0)

    if args.count:
        with open(JSON_FILE) as f:
            data = json.load(f)
            print(len(data["sites"]))
            f.close()
            exit(0)

    if args.list:
        with open(JSON_FILE) as f:
            data = json.load(f)
            names = []
            urls = {}
            longest_len = 0
            for _, el in enumerate(data["sites"]):
                names.append(el["name"])
                urls[el["name"]] = el["manga_url"]
                longest_len = max(longest_len, len(el["name"]))

            for name in sorted(names):
                print(name.ljust(longest_len + 5), urls[name])

            f.close()
            exit(0)

    with open(JSON_FILE) as f:
        data = check_for_updates(f)
        update_json(data)
        f.close()
        exit(0)


if __name__ == "__main__":
    main()
