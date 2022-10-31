import time
import csv

import requests

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from settings_chrome import driver


def create_csv_game_mode(additions):
    with open("result/games_additions.csv", mode="a", encoding='utf-8') as w_file:
        titles = [
            'name',
            'addition',
            'addition_price',
        ]
        for addition in additions:
            if addition is not None:
                for addition_game in addition:
                    file_writer = csv.DictWriter(w_file, delimiter=",", lineterminator="\r", fieldnames=titles)
                    file_writer.writeheader()
                    file_writer.writerow(addition_game)


def create_csv_game(games):
    with open("result/games.csv", mode="a", encoding='utf-8') as w_file:
        titles = [
            'name',
            'description',
            'release_date',
            'main_price',
            'sale',
            'sale_price',
        ]
        for game in games:
            file_writer = csv.DictWriter(w_file, delimiter=",", lineterminator="\r", fieldnames=titles)
            file_writer.writeheader()
            file_writer.writerow(game)


def parce_games_addition(response, game_name):
    soup = BeautifulSoup(response.text, 'html.parser')

    section_mode = soup.select('[aria-label="Дополнения для этой игры"]')
    if section_mode:
        titles_addition = section_mode[0].select('.ProductCard-module__title___3iwfs')
        prices_addition = section_mode[0].select('.ProductCard-module__price___Ocr3o')

        addition_game = []

        for title, price in zip(titles_addition, prices_addition):
            addition = {
                'name': game_name,
                'addition': title.get_text(),
                'addition_price': price.get_text(),
            }

            addition_game.append(addition)

        return addition_game


def parce_games():
    time.sleep(7)
    game_cards = driver.find_elements(By.CLASS_NAME, 'gameDivLink')
    game_links = [link.get_attribute('href') for link in game_cards]

    games = []
    additions = []

    for link in game_links:
        try:
            response = requests.get(link)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')

            name = soup.find('h1')
            description = soup.find('div', class_='Description-module__descriptionContainer___3gH-q')
            release_date = soup.find('div', class_='Description-module__details___1w_c0')
            price = soup.find('span', class_='Price-module__srOnly___2mBg_')

            game = {
                'name': name.get_text(),
                'description': description.get_text(),
                'release_date': release_date.get_text().split('Дата выпуска')[1],
            }

            if ',' in price.get_text():
                main_price = price.get_text().split(',')[0].split('USD')[1]
                sale_price = price.get_text().split(',')[1].split('USD')[1]
                game['main_price'] = main_price
                game['sale'] = 1
                game['sale_price'] = sale_price

            else:
                game['main_price'] = price.get_text().split('USD')[1]
                game['sale'] = 0
                game['sale_price'] = 0

            games.append(game)
            additions.append(parce_games_addition(response, name.get_text()))

        except (requests.exceptions.HTTPError, AttributeError) as error:
            print(error)

    create_csv_game(games)
    create_csv_game_mode(additions)


def main():
    url_catalog_games = 'https://www.xbox.com/ru-RU/games/all-games'
    driver.get(url_catalog_games)
    driver.implicitly_wait(30)

    driver.find_element(By.CSS_SELECTOR,
                        '#ContentBlockList_1 > div.thecatalog > div.gameList >'
                        ' div.paginateControl > section > div > div > button').click()  # number of games button
    driver.find_element(By.XPATH,
                        '/html/body/div[1]/div/div/div[3]/div/div/div/div[2]'
                        '/div[1]/div[1]/div[2]/div[7]/section/div/div/ul/li[3]').click()  # item 100 games per page
    driver.implicitly_wait(30)

    parce_games()

    for page in range(2, 6):
        print(f'number page{page}')
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[3]/div/div/div/div[2]/div[1]'
                                      '/div[1]/div[2]/nav/ul/li[31]/a').click()  # button next page
        driver.implicitly_wait(30)
        parce_games()

    driver.quit()


if __name__ == '__main__':
    main()
