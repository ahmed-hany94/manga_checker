import requests
from bs4 import BeautifulSoup as bs4
import json
import argparse
import pprint
import re

JSON_FILE = "./site_obj.json"

MIN_MANGA_PANEL = 3

pp = pprint.PrettyPrinter(indent=4)


def check_for_updates(file):
    data = json.load(file)
    for el in data:
        idx = el["idx"]
        manga_url = el["manga_url"]
        url = el["url"]
        name = el["name"]
        css_selector = el["css_selector"]

        try:
            r = requests.get(manga_url)
            text = r.text
            soup = bs4(text, "lxml")

            if r.ok:
                last_entry_url = soup.select(css_selector)[0]["href"]
                if not last_entry_url.startswith("https"):
                    last_entry_url = (
                        re.match("(https*:\/\/.*?)\/", url).group(1) + last_entry_url
                    )
                if url == last_entry_url:
                    print(f"{idx}- Nothing new (-_-)")
                else:
                    r = requests.get(last_entry_url)
                    soup = bs4(r.text, "lxml")
                    if len(soup.find_all("img")) > MIN_MANGA_PANEL:
                        print(
                            f"{idx}- Manga Update Found: \t\t"
                            + name
                            + "\t\t"
                            + last_entry_url
                        )
                        el["url"] = last_entry_url
                    else:
                        print(f"{idx}- Nothing new (-_-)")
        except requests.exceptions.RequestException as e:
            print(e)
        except IndexError as e:
            print(e)
            print(url)
            print()
        except KeyboardInterrupt:
            exit(0)
    return data


def add_manga():
    try:
        with open(JSON_FILE) as f:
            data = json.load(f)
            m = input("manga_url: ")
            n = input("name: ")
            u = input("url: ")
            c = input("css selector: ")
            if m and n and u:
                idx = len(data)
                data.append(
                    {
                        "idx": idx,
                        "manga_url": m,
                        "name": n,
                        "url": u,
                        "css_selector": c,
                    }
                )
                print("Saved")
            else:
                print("Error, not saved!!")
            f.close()
    except KeyboardInterrupt:
        exit(0)

    return data


def delete_manga():
    try:
        list_manga(sort=False)
        index = input("index: ")
        with open(JSON_FILE) as f:
            data = json.load(f)
            del data[int(index)]
            f.close()
    except KeyboardInterrupt:
        exit(0)

    return data


def list_manga(sort=False):
    with open(JSON_FILE) as f:
        data = json.load(f)
        names = []
        urls = {}
        longest_len = 0
        i = 0

        for _, el in enumerate(data):
            names.append(el["name"])
            urls[el["name"]] = el["manga_url"]
            longest_len = max(longest_len, len(el["name"]))

        if sort:
            for name in sorted(names):
                print(str(i) + "- " + name.ljust(longest_len + 5), urls[name])
                i += 1
        else:
            for name in names:
                print(str(i) + "- " + name.ljust(longest_len + 5), urls[name])
                i += 1

        print()
        f.close()


def update_json(data):
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=4)
        f.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--add_manga", help="add new manga", action="store_true")
    parser.add_argument(
        "-d", "--delete_manga", help="delete existing manga", action="store_true"
    )
    parser.add_argument("-c", "--count", help="how many manga", action="store_true")
    parser.add_argument("-l", "--list", help="list manga_sites", action="store_true")
    parser.add_argument(
        "-la",
        "--list-alphabetically",
        help="list manga_sites alphabetically",
        action="store_true",
    )
    args = parser.parse_args()

    if args.add_manga:
        data = add_manga()
        update_json(data)
        exit(0)

    if args.delete_manga:
        data = delete_manga()
        update_json(data)
        exit(0)

    if args.count:
        with open(JSON_FILE) as f:
            data = json.load(f)
            print(len(data))
            f.close()
            exit(0)

    if args.list:
        list_manga(sort=False)
        exit(0)

    if args.list_alphabetically:
        list_manga(sort=True)
        exit(0)

    with open(JSON_FILE) as f:
        data = check_for_updates(f)
        update_json(data)
        f.close()
        exit(0)


if __name__ == "__main__":
    main()
