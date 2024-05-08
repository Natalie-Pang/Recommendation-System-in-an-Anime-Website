# Develop a Comprehensive Anime Website with Personalised Recommendation System

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Testing](#testing)

# Introduction
This anime website is developed to address the problem of lack of personalised recommendation system and to facilite the mental well-being of anime fans. This website has these main features:
Feature|Description
-------|-----------
Recommendation|By entering an anime, a list of anime with similar hypothesis will be generated.
AnimeList|In this page, you can browse all animes. You can search by name or filter by genres.
Discussion|In the discussion forum, you can either create a new discussion, or join an existing discussion to chat with others.
Anaylsis|In this page, different graphs related to anime, such as growth of anime and most popular genres, will be displayed with detailed description. 
Event|In this page, data gathered from web crawling are displayed
Account|You can register, log in, or log out here. If you have created an account, you can change your profile picture.


### Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install all required packages for the script in terminal.
```bash
pip install -r website/requirements.txt
```
``` bash
playwright install chromium
```

# Usage
To run the website, please enter the following in the terminal:
```bash
python main.py
```
If the above command does not work, pleas try the following in the terminal:
```bash
python3 main.py
```

# Testing
A test file is created to test if all url are working properly.
The test file is located at the tests folder. To run the test, simply enter the follow command in the terminal
```bash
coverage run -m pytest -v
```
If all tests pass it will show PASSES.

To check the coverage of each html, run the following command in the terminal
```bash
coverage run -m pytest
```
```bash
coverage reoport
```
```bash
coverage report --omit=web_crawling.py 
```
