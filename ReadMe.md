# Hydr0 Scraper
Hydr0 Scraper is a Python application designed to scrape download links from the webpage [hydr0.org](https://hydr0.org). While it could be theoretically used for accessing copyrighted materials, the intention behind this project is to demonstrate web scraping techniques and provide a fun learning experience rather than promote piracy.

## Installation
To install and run Hydr0 Scraper, follow these steps:

### Clone the repository:

    git clone https://github.com/your_username/mp3scraper.git
    cd hydr0-loader

### Create a virtual environment:

    python3 -m venv env
###  Activate the virtual environment:

#### On Windows:
    .\env\Scripts\activate
#### On macOS and Linux:

    source env/bin/activate
#### Install the required packages:

pip install -r requirements.txt

#### Run Hydr0 Scraper:
    ./hyrd0_scraper.py
    
# How it Works

Hydr0 Scraper utilizes web scraping techniques to extract download links from [hydr0.org](https://hydr0.org) for educational purposes. By analyzing the HTML structure of the webpage, the application locates relevant information and presents it in a user-friendly manner.

## 1. Put a all tracks you want to scrape in the tracks.txt file

Each track you would like to download you have to put in the `tracks.txt` file.
One line for each track, like this:

    Woqlz - Hazard
    Rompasso - Angetenar
    The Pattern Forms - Black Rain

## 2. Run the scraper

Run the python script:

    python3 hydr0_scraper.py

## 3 Select the song(s) you would like to download

For each song in the `tracks.txt` file the scraper will run a search on the [hydr0.org]
(https://hydr0.org) website. The result of this search will be presented to the command line interface (CLI). Here you can select one, multiple or none of the tracks.

### Here is an example:

    Search results for: Rompasso - Angetenar

    0 made for hayasa - Rompasso - Angetenar (MSMV Remix) 3:40
    1 Rompasso - Angetenar 6:06
    2 Rompasso - Angetenar 4:47
    3 Rompasso - Angetenar 3:06
    4 [33-39Hz] Rompasso - Angetenar 6:05
    5 Rompasso, Rich The Kid - Angetenar 3:10
    6 ROMPASSO - ANGETENAR (DEITIES Remix) 2:59
    7 Rompasso - Angetenar (TIAN.RON JUN remix) 3:27
    8 Rompasso - Angetenar 3:36
    9 Rompasso - Angetenar 5:13
    10 Rompasso - Angetenar (slowed) 5:39

    Which should be downloaded? Please enter the respective number.
    You can pick multiple tracks separated with a whitespace like this:4 12 15
    If you don't want to download anything. Please write 'n':

Now we would like to scrape the second song, as its fits our search the best.
Therefore we enter:

    1

into the CLI.

However, If we would also like to scrape the Deities Remix, we can enter:

    1 6

So to scrape multiple songs from the search list,
we just enter the respective number with a space between them.

If none if the results is what we were searching for we just enter a `n` to the CLI.

## 4 Scraping of the urls
For our selection the program will extract the url to the respective mp3 file
and write it - together with artist and title to the scraped.txt file.

## 5 Download the files
After scraping the urls you can run:

    ./hyrd0_scraper.py -f 'scraped.txt'

To download the mp3 files from using the scraped URLs.

Alternatively, when running the Hydr0 scraper with the `-d` flag, the urls are not only written to the `scraped.txt` file, the file are also downloaded to the users `Downloads` directory using from the scraped urls.

#### Example:

    ./hydr0_scraper -d

Please note that while the tool facilitates access to files hosted on the website, it's essential to use it responsibly and legally. Respect intellectual property rights and ensure that you have the necessary permissions to download and use the files. This tool is intended for educational purposes only, and the developers do not endorse or encourage any illegal activities, including piracy.

# Disclaimer

While Hydr0 Scraper can technically be used to access copyrighted materials, the project is intended for educational purposes only. The developers do not endorse or encourage any illegal activities. Please respect intellectual property rights and use this tool responsibly.

Feel free to adjust the content according to your preferences and add any additional sections or information you think might be relevant.