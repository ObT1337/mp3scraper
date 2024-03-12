#! python3
import argparse
import asyncio
import logging
import os
import re
import threading
from pathlib import Path
from queue import Queue

import aiofiles
import aiohttp
import requests
from bs4 import BeautifulSoup
from mutagen.easyid3 import EasyID3

log = logging.getLogger(__file__)
log.setLevel(logging.DEBUG)
info_handler = logging.StreamHandler()
info_handler.setLevel(logging.DEBUG)

# create formatter
info_formatter = logging.Formatter("%(levelname)s: %(asctime)s - %(message)s")

# add formatter to ch
info_handler.setFormatter(info_formatter)

# add ch to logger
log.addHandler(info_handler)
TRACKS_TXT = "tracks.txt"
MISSING_TXT = "missing.txt"
SCRAPED_TXT = "scraped.txt"
URLS_TXT = "url.txt"


class Track:
    def __init__(
        self, id=None, artist=None, title=None, duration=None, url=None
    ) -> None:
        self.id = id
        self.artist = artist
        self.title = title
        self.duration = duration
        self.url = url
        self.filetype = "mp3"
        self._filename = f"{self.artist} - {self.title}.{self.filetype}"

    def __str__(self) -> str:
        return f"{self.id}\t{self.artist} - {self.title}\t{self.duration}"

    def artist_title(self) -> str:
        return f" {self.artist} - {self.title}"

    def with_url(self) -> str:
        return f"{self.artist} - {self.title}\t{self.duration}\t{self.url}"

    @property
    def filename(self) -> str:
        return self._filename

    @filename.setter
    def filename(self, value):
        self._temperature = value


class TrackDownloader:
    def __init__(self, queue: Queue, name):
        self.name = str(name)
        self.queue = queue
        self.download_thread = threading.Thread(target=self.start_download)
        self.download_thread.start()

    def start_download(self):
        asyncio.run(self.download_loop())

    async def download_loop(self):
        log.debug("Worker %s: Ready!", self.name)
        while True:
            track = self.queue.get()
            if track is None:
                log.debug("Shutdown: %s", self.name)
                self.queue.task_done()
                break
            await self.download(track)
            self.queue.task_done()

    async def download(self, track: Track):
        log.debug("%s: Will start downloading track: %s", self.name, track.with_url())
        try:
            downloads_dir = os.path.join(str(Path.home()), "Downloads")
            os.makedirs(downloads_dir, exist_ok=True)

            async with aiohttp.ClientSession() as session:
                async with session.get(track.url) as response:
                    if response.status == 200:
                        mp3_path = os.path.join(downloads_dir, track.filename)
                        async with aiofiles.open(mp3_path, "wb") as f:
                            # Read the response data and fully consume it
                            async for chunk in response.content.iter_any():
                                await f.write(chunk)
                        log.info("%s: Downloaded and saved: %s", self.name, mp3_path)
                        self.write_scraped(track.with_url() + "\n")
                        self.write_id3_tags(mp3_path, track)
                    else:
                        self.write_missing(track.artist_title() + "\n")
                        log.warning("%s: Failed to download: %s", self.name, track.url)

        except aiohttp.client_exceptions.ClientPayloadError as e:
            log.error("%s: Response payload is not completed: %s", self.name, str(e))
        except Exception as e:
            log.error(
                "%s: An error occurred while downloading track: %s", self.name, str(e)
            )
            log.debug("%s: Exception type is: %s", self.name, str(type(e)))

    @staticmethod
    def write_id3_tags(mp3_path, track: Track):
        try:
            mp3 = EasyID3(mp3_path)
            mp3["artist"] = track.artist
            mp3["title"] = track.title
            mp3.save()
        except Exception as e:
            log.error("An error occurred while writing ID3 tags: %s", str(e))

    @staticmethod
    def write_scraped(value: str):
        try:
            with open(SCRAPED_TXT, "a+") as f:
                f.write(value)
        except Exception as e:
            log.error("An error occurred while writing to scraped.txt: %s", str(e))
            log.debug("Exception type is: %s", str(type(e)))

    @staticmethod
    def write_missing(value: str):
        try:
            with open(MISSING_TXT, "a+") as f:
                f.write(value)
        except Exception as e:
            log.error("An error occurred while writing to missing.txt: %s", str(e))
            log.debug("Exception type is: %s", str(type(e)))

    @staticmethod
    def write_url(value: str):
        try:
            with open(URLS_TXT, "a+") as f:
                f.write(value)
        except Exception as e:
            log.error("An error occurred while writing to url.txt: %s", str(e))
            log.debug("Exception type is: %s", str(type(e)))


class Hydr0Browser:
    def __init__(self):
        self.baseurl = "hydr0.org"
        self.protocol = "https://"
        # self.add_block_version = self.get_add_block_version()
        self.session = requests.Session()

    @staticmethod
    def format_track_name(track: str):
        cleaned_track = re.sub(r"-+", "-", track)
        cleaned_track = re.sub(r"[^\w\s-]", "", cleaned_track)
        cleaned_track = re.sub(r"\s+", "-", cleaned_track)
        cleaned_track = cleaned_track.strip("-")
        return cleaned_track

    def load_results(self, track: str, location: str = "normal"):
        try:
            track = Hydr0Browser.format_track_name(track)
            if location == "normal":
                url = f"{self.protocol}{track}.{self.baseurl}"
            elif location == "artist":
                url = f"{self.protocol}{self.baseurl}/artist/{track}/"
            else:
                log.error("This location is not yet implemented!")
                return []
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            result = soup.find(id="xx1")

            playlist = result.find("ul", class_="playlist")
            res = []
            if playlist:
                for id, row in enumerate(playlist.find_all("li")):
                    left = row.find(class_="playlist-left")
                    right = row.find(class_="playlist-right")
                    file_source_element = left.find("a", class_="playlist-play no-ajax")
                    url = file_source_element.get("data-url")
                    artist = left.find(
                        "span", class_="playlist-name-artist"
                    ).text.strip()
                    title = left.find("span", class_="playlist-name-title").text.strip()
                    duration = right.find(
                        "span", class_="playlist-duration"
                    ).text.strip()

                    track = Track(id, artist, title, duration, url)
                    res.append(track)
        except requests.exceptions.InvalidURL as e:
            log.error("Invalid URL: %s", str(e))
            return False
        except Exception as e:
            log.error("An error occurred while loading results: %s", str(e))
            log.debug("Exception type is: %s", str(type(e)))
            return False

        return res


def define_tracks(queue: Queue, download=False):
    browser = Hydr0Browser()

    def add_to_queue(track: Track):
        queue.put(track)
        log.debug("Added Track to que: %s", track)

    with open(TRACKS_TXT, "r") as f:
        for line in f:
            browser.load_results(line)
            res = browser.load_results(line)
            if not res:
                res = browser.load_results(line, "artist")
            if not res:
                TrackDownloader.write_missing(line)
                continue
            print(f"\nSearch results for: {line}")
            for track in res:
                print(track)
            skip = False
            track = None
            bad_choice = False
            while not skip:
                user_input = input(
                    "\nWhich should be downloaded? Please enter the respective number.\n"
                    "You can pick multiple tracks separated with a whitespace like this:4 12 15\n"
                    "If you don't want to download anything. Please write 'n':\n"
                )

                def invalid_input(choice):
                    log.error(
                        "Please enter a number or 'n'! %s is not a valid choice!",
                        choice,
                    )

                choices = user_input.split(" ")
                log.debug("Choices is of len %d", len(choices))
                if len(choices) == 1 and choices[0] is None:
                    invalid_input(choices[0])

                tracks = []
                for choice in choices:
                    if choice is None:
                        continue
                    log.debug("Choice is %s", choice)
                    if choice.isdigit():
                        track: Track = res[int(choice)]
                        tracks.append(track)
                        TrackDownloader.write_url(track.url + "\n")
                        continue
                    if choice == "n":
                        log.info("None will be downloaded, continue")
                        skip = True
                        break
                    invalid_input(choice)
                    bad_choice = True
                    break
                if bad_choice:
                    skip = False
                    bad_choice = False
                    continue
                break

            if skip:
                TrackDownloader.write_missing(line)
                continue

            if download:
                for track in tracks:
                    add_to_queue(track)
            else:
                TrackDownloader.write_scraped(track.with_url() + "\n")


def main(n=5, download=False):
    log.debug("Testing if debug is working!")
    log.debug("Download is set to: %s", str(download))
    download_queue = Queue()
    if download:
        [TrackDownloader(download_queue, i) for i in range(n)]
    define_tracks(download_queue, download)
    if download:
        [download_queue.put(None) for _ in range(n)]
        download_queue.join()


def download_from_txt(file, n=5):
    download_queue = Queue()
    with open(file, "r") as f:
        for line in f:
            line = line.split("\t")
            if len(line) < 3:
                continue
            artist_title, duration, url = line
            artist, title = artist_title.split(" - ")[:2]
            track = Track(artist=artist, title=title, duration=duration, url=url)
            download_queue.put(track)
    [TrackDownloader(download_queue, i) for i in range(n)]
    [download_queue.put(None) for _ in range(n)]
    download_queue.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process tracks and download them.")
    parser.add_argument("-f", "--file", help="Path to the file containing tracks.")
    parser.add_argument("-n", "--nodes", help="number of nodes", type=int, default=5)
    parser.add_argument(
        "-d",
        "--download",
        action="store_true",
    )
    args = parser.parse_args()

    if args.file:
        download_from_txt(args.file, args.nodes)
    else:
        main(args.nodes, args.download)
