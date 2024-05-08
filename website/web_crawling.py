import time
from playwright.sync_api import sync_playwright
import pandas as pd

def get_top_anime_data():
    with sync_playwright() as p:

        page_url = 'https://www.imdb.com/search/title/?keywords=anime'

        browser = p.chromium.launch(headless=False)
        
        page = browser.new_page()
        page.set_default_timeout(0)
        page.goto(page_url)

        top_anime_list = []

        animes = page.locator('.ipc-metadata-list-summary-item').all()

        for anime in animes:
            anime_dict = {}
            # event_dict['name'] = anime.locator('.ipc-title-link-wrapper .ipc-title__text').inner_text().lstrip('0123456789. ')
            anime_dict['name'] = anime.locator('.ipc-title-link-wrapper .ipc-title__text').inner_text()
            anime_dict['years'] = anime.locator('//div[@class="sc-b0691f29-7 hrgukm dli-title-metadata"]/span[1]').inner_text()
            anime_dict['rating'] = anime.locator('//span[@data-testid="ratingGroup--imdb-rating"]').inner_text().split('\n')[0]
            anime_dict['image_url'] = anime.locator('img.ipc-image').get_attribute('src')
            anime_dict['description'] = anime.locator('.ipc-html-content-inner-div').inner_text()
            anime_dict['url'] = f'https://www.imdb.com/{anime.locator('.ipc-title-link-wrapper').get_attribute('href')}'
            top_anime_list.append(anime_dict)

        print(top_anime_list)
        browser.close()
        df = pd.DataFrame(top_anime_list)
        df.to_csv('./website/static/data/top_anime.csv', index=False)

def get_event(location):
    with sync_playwright() as p:
        browser = p.chromium.launch()

        page_url = f'https://www.google.com/search?q=anime+events+in+{location}&ibp=htl;events&hl=en&gl=US'
        browser = p.chromium.launch(headless=False)
        
        page = browser.new_page()
        page.set_default_timeout(0)
        page.goto(page_url)

        # Reject google cookies
        if page.url.startswith("https://consent.google.com"):
            reject_button = page.get_by_role("button", name="Reject all")
            reject_button.click()
        
        # Wait for the search results to load
        page.wait_for_selector('.PaEvOc', state='visible')

        # Get event details
        event_list = []
        events = page.locator(".scm-c").all()

        for event in events:
            event_dict = {}
            event_dict['title'] = event.locator('.dEuIWb').inner_text()
            event_dict['start_date'] = f'{event.locator('.FTUoSb').inner_text()} {event.locator('.omoMNe').inner_text()}'
            event_dict['location'] = event.locator('.ov85De').first.inner_text()
            event_dict['event_image_url'] = event.locator('.YQ4gaf').get_attribute('src')
            for x in event.locator('.PVlUWc').all():
                event_dict['description'] = x.inner_text()
            for y in event.locator('a.zTH3xc').all():
                event_dict['url'] = y.get_attribute('href')
            event_list.append(event_dict)
        browser.close()
        print(len(events))
        # print(event_list)
        df = pd.DataFrame(event_list)
        df.to_csv('./website/static/data/event.csv', index=False)

def get_music_data():
    with sync_playwright() as p:

        page_url = 'https://animesongs.org/songs'

        browser = p.chromium.launch(headless=False)
        
        page = browser.new_page()
        page.set_default_timeout(0)
        page.goto(page_url)

        page_counter = 0
        max_page = 5

        music_list = []
        page.wait_for_selector('.search-song')
        # musics = page.locator('.search-song').all()

        while page_counter < max_page:
            time.sleep(7)
            musics = page.locator('.search-song').all()

            for music in musics:
                music_dict = {}
                info = music.locator('.search-song__info').inner_text()
                year, anime_title = info.split(', ', 1)
                music_dict['song_title'] = music.locator('.search-song__title').inner_text()
                music_dict['anime_title'] = anime_title
                music_dict['image'] = music.locator('.search-song__image').get_attribute('src')
                music_dict['singer'] = music.locator('.search-song__performer').inner_text()
                music_dict['year'] = year
                music_list.append(music_dict)

            next_page_button = page.locator('.complex-search-pagination__link').get_by_text('Next')
            if not next_page_button:
                break

            next_page_button.click()
            page_counter += 1

        print(len(musics))
        print(music_list)
        browser.close()
        df = pd.DataFrame(music_list)
        df.to_csv('./website/static/data/music_list.csv', index=False)
