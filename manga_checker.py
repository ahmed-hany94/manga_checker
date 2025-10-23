import re
import json
import requests
from bs4 import BeautifulSoup as bs4
from pathlib import Path
from typing import Dict

# --------- #
# Constants #
# --------- #

DB_FILE = Path("site_obj.json")

# ------- #
# Classes #
# ------- #

class BaseSite():
    def __init__(self, index, manga_name, attrs_ref):
        self.index = index
        self.manga_name = manga_name
        self.attrs = attrs_ref
        self.manga_url = None
        self.manga_num = None
        self.chapter_url = None
        self.chapter_num = None
        self.has_updates = False
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.mangakakalot.gg/",
        }

    def _fetch_latest(self):
        raise NotImplementedError

    def _print_success(self):
        raise NotImplementedError
    
    @staticmethod
    def print_nothing_new(index):
        print(f"{index}- Nothing new (-_-)")

    def _is_chapter_ids_different(self, old, new):
        return old != new

class Mangadex(BaseSite):
    def __init__(self, index, manga_name, attrs_ref):
        super().__init__(index, manga_name, attrs_ref)
        self.manga_id = self.attrs["manga_id"]
        self.lang = self.attrs["lang"]
        self.chapter_id = self.attrs["chapter_id"]
        self.chapter_num = self.attrs["chapter_num"]
        self.api_url = self._api_url()
        self._fetch_latest()

    def _api_url(self):
        if self.manga_id:
            return f"https://api.mangadex.org/manga/{self.manga_id}/feed?translatedLanguage[]={self.lang}&order[chapter]=desc&limit=1"
        else:
            print("Missing `manga_id` attribute to create manga_url")

    def _print_success(self):
        print(
            f"{self.index}- Manga Update Found: \t\t"
            + self.manga_name
            + "\t\t"
            + self.chapter_url
        )

    def _fetch_latest(self):
        try:
            r = requests.get(self.api_url)
            assert r.ok, f"API fetch failed for {self.manga_name}"
            data = r.json()
            assert len(data["data"]) != 0, f"data is empty {data}"
            data = data["data"][0]
            latest_chapter_id = data["id"]
            latest_chapter_num = data["attributes"]["chapter"]
            if self.chapter_url == "" or later_than(self.chapter_num, latest_chapter_num) or self._is_chapter_ids_different(self.chapter_id, latest_chapter_id):
                # Different, so we mutate
                self.has_updates = True
                self.attrs["chapter_id"] = self.chapter_id = latest_chapter_id
                self.attrs["chapter_num"] = self.chapter_num = latest_chapter_num
                self.manga_url = f"https://mangadex.org/title/{self.manga_id}/"
                self.chapter_url = f"https://mangadex.org/chapter/{self.chapter_id}"
        except Exception as e:
            print(f"{self.index}- Mangadex Error: {self.manga_name}'s {e}")

class Mangakakalot(BaseSite):
    def __init__(self, index, manga_name, attrs_ref):
        super().__init__(index, manga_name, attrs_ref)
        self.manga_url = self.attrs["manga_url"]
        self.chapter_url = self.attrs["chapter_url"]
        self.chapter_num = self.attrs["chapter_num"]
        self.selector = self.attrs["selector"]
        self.latest_chapter = self._fetch_latest()
    
    def _print_success(self):
        print(
            f"{self.index}- Manga Update Found: \t\t"
            + self.manga_name
            + "\t\t"
            + self.chapter_url
        )

    def _get_latest_chapter_number(self, latest_chapter_url):
        match = re.search(r'chapter-([\d\-]+)', latest_chapter_url)
        if match:
            chapter_str = match.group(1)
            parts = chapter_str.split('-')
            if len(parts) == 2:
                return f"{parts[0]}.{parts[1]}"
            else:
                return parts[0]

    def _fetch_latest(self):
        try:
            r = requests.get(self.manga_url, headers=self.headers)
            text = r.text
            soup = bs4(text, "lxml")
            assert r.status_code == 403, f"Cloudflare shenanigans for {self.manga_name}"
            if r.ok:
                latest_chapter_url = soup.select(self.selector)[0]["href"]
                latest_chapter_num = self._get_latest_chapter_number(latest_chapter_url)
                if latest_chapter_num == "" or later_than(self.chapter_num, latest_chapter_num):
                    self.has_updates = True
                    self.attrs["chapter_url"] = self.chapter_url = latest_chapter_url
                    self.attrs["chapter_num"] = self.chapter_num = latest_chapter_num               
        except Exception as e:
            print(f"{self.index}- {self.manga_name} - Mangakakalot Error: {e}")

class Database:
    def __init__(self, path: Path = DB_FILE):
        self.path = path
        self.data = self._load()

    def _load(self) -> Dict:
        if not self.path.exists():
            print("Error: DB_FILE path doesn't exist")
            exit(-1)
        try:
            with open(self.path, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Error: reading DB_FILE file failed")
            exit(-1)

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

# --------- #
# Functions #
# --------- #

def later_than(first, second):
    if first == '':
        return True
    return float(first) < float(second)

def check_for_updates(db: Database):
    for index, (manga_name, manga_data) in enumerate(db.data.items(), start=1):
        if "mangadex" in manga_data and manga_data["mangadex"]:
            mangadex = Mangadex(index, manga_name, manga_data["mangadex"])
        
        if "mangakakalot" in manga_data and manga_data["mangakakalot"]:
            mangakakalot = Mangakakalot(index, manga_name, manga_data["mangakakalot"])

        # TODO: fix the missing `updated_site` property
        if mangadex.has_updates and later_than(mangakakalot.chapter_num, mangadex.chapter_num):
            manga_data["updated_site"] = "mangadex"
            mangadex._print_success()   
        elif mangakakalot.has_updates and later_than(mangadex.chapter_num, mangakakalot.chapter_num):
            manga_data["updated_site"] = "mangakakalot"
            mangakakalot._print_success()
        else:
            BaseSite.print_nothing_new(index)

def list_manga(db: Database, sort: bool = False, latest: bool = False):
    names = []
    urls = {}
    longest_len = 0
    data = db.data

    for (manga_name, manga_data) in data.items():
        names.append(manga_name)
        updated_site = manga_data["updated_site"]
        urls[manga_name] = [manga_data[updated_site]["chapter_num"]]
        longest_len = max(longest_len, len(manga_name))

    def print_formatted(list, l=0):
        print("Manga Name" + (longest_len - 1)
              * ' ' + " | " + "Chapter Number")
        print("=" * (longest_len + 26))
        for index, name in enumerate(list):
            i = str(index + 1).ljust(len(str(len(data))))
            spacing = longest_len + 5
            print(f"{i}- {name.ljust(spacing)} | {urls[name][l]}")
        print("=" * (longest_len + 26))

    if sort:
        if latest:
            print_formatted(sorted(names), 1)
        else:
            print_formatted(sorted(names))
    else:
        if latest:
            print_formatted(names, 1)

        else:
            print_formatted(names)

    print()


def add_interactive(db: Database):
    # TODO: fix different name extraction for same manga for different .
    #       example: Kusuriya no Hitorigoto & The Apothecary Diaries.
    try:
        while True:
            manga_url = input(f"Enter manga url: ")
            if "mangakakalot" in manga_url:
                site_name = "mangakakalot"
                manga_name = manga_url.split('/')[-1].replace("-", " ").title()
                db.data[manga_name] = {}
                db.data[manga_name][site_name] = {}
                db.data[manga_name][site_name]["manga_url"] = manga_url
                db.data[manga_name][site_name]["chapter_url"] = ""
                db.data[manga_name][site_name]["chapter_num"] = ""
                db.data[manga_name][site_name]["selector"] = "#chapter > div > div.chapter-list > div:nth-of-type(1) > span:nth-of-type(1) > a"
            elif "mangadex" in manga_url:
                site_name = "mangadex"
                manga_url = manga_url.split('?')[0]
                manga_name = manga_url.split('/')[-1]
                manga_name = manga_name.replace("-", " ").title()
                db.data[manga_name] = {}
                db.data[manga_name][site_name] = {}
                db.data[manga_name][site_name]["manga_id"] = manga_url.split('/')[4]
                db.data[manga_name][site_name]["lang"] = "en"
                db.data[manga_name][site_name]["chapter_id"] = ""
                db.data[manga_name][site_name]["chapter_num"] = ""
            else:
                print(f"Only mangakakalot.com & mangadex.com are supported. {manga_url}")

            answer = input("Add another manga?! (y|n): ")
            if answer.lower() == "n":
                break
    except KeyboardInterrupt:
        print("\n\nInterrupted!")
        exit(0)

def delete_interactive(db: Database):
    pass

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Manga Checker")
    parser.add_argument("-c", "--count", action="store_true", help="Manga Count")
    # -e is reserved for the batch file used in calling this to edit it
    parser.add_argument("-e", "--edit-code", action="store_const", const=None, help="Open in VSCode")
    parser.add_argument("-l", "--list", action="store_true", help="List Manga Sites")
    parser.add_argument("-la", "--list-alphabetically", action="store_true", help="List Manga Sites Alphabetically")
    parser.add_argument("-L", "--latest", action="store_true", help="List Latest Manga Chapters Urls")
    parser.add_argument("-n", "--new", action="store_true", help="Add Manga")
    args = parser.parse_args()
    
    db = Database()

    try:
        if args.new:
            add_interactive(db)
            db.save()
        elif args.count:
            print(len(db.data))
            exit(0)
        elif args.list:
            list_manga(db)
            exit(0)
        # elif args.delete:
        #     delete_interactive(db)
        #     db.save()
        # elif args.list or args.sort:
        #     list_manga(db, sort=args.sort)
        # elif args.count:
        #     print(f"Total: {len(db.get_manga())}")

        check_for_updates(db)
        db.save()
    except KeyboardInterrupt:
        print("\n\nInterrupted!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
