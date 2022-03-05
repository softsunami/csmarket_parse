import requests
import configparser
import json
from bs4 import BeautifulSoup
from time import sleep

config = configparser.ConfigParser()  # Создаем объекст парсера
config.read("config.ini", encoding='utf-8')  # читаем конфиг


def fixqul(msg):
    return str(bytes(msg, encoding="utf-8")).replace("\\", "%").replace("x", "").upper()[2:-1]


def loadcfg(configq):
    res = {
        "price_min": int(configq["cfg"]["price_min"]),
        "price_max": int(configq["cfg"]["price_max"]),
        "rare_type": fixqul(configq["cfg"]["rare_type"]),
        "quality": fixqul(configq["cfg"]["quality"]),
    }
    if res["price_min"] >= res["price_max"]:
        print("Неверно указан ценовой диапазон")
        exit(-1)
    return res


choice = input("Сменить конфиг: y/n?\n")


if choice == 'y':
    config["cfg"]["price_min"] = input("Минимальная цена: ")
    config["cfg"]["price_max"] = input("Максимальная цена: ")
    config["cfg"]["rare_type"] = input("Раритетность: ")
    config["cfg"]["quality"] = input("Качество: ")
    with open("config.ini", "w", encoding="utf-8") as file:
        config.write(file)
    saved_cfg = loadcfg(config)
else:
    saved_cfg = loadcfg(config)

with open("res.json", "w"):
    pass


page = 1  # Текущая страница

url = f"https://market.csgo.com/?s=pop&r={saved_cfg['rare_type']}&" \
      f"q={saved_cfg['quality']}&p={page}&rs={saved_cfg['price_min']};{saved_cfg['price_max']}&sd=desc".replace(" ", "%20")

headers = {
    "accept": "*/*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
}
response = requests.get(url=url, headers=headers).text
soup = BeautifulSoup(response, "lxml")
pages = int(soup.find('div', class_="w33 notresize page-counter").find("span").text)  # Количество страниц

result = []
card_dict = {}

for page in range(1, pages+1):
    url = f"https://market.csgo.com/?s=pop&r={saved_cfg['rare_type']}&" \
          f"q={saved_cfg['quality']}&p={page}&rs={saved_cfg['price_min']};{saved_cfg['price_max']}&sd=desc".replace(" ", "%20")
    soup = BeautifulSoup(response, "lxml")
    items_list = soup.find("div", class_="market-items").find_all("a", class_="item hot")
    for item in items_list:
        try:
            href = "https://market.csgo.com" + item.get("href")
        except:
            href = ""
        try:
            price = item.find("div", class_="price").text.replace(" ", "р")
        except:
            price = ""
        try:
            name = item.find("div", class_="name").text.strip()
        except:
            name = ""
        try:
            stickers = item.find("div", class_="i-inscribed").find_all("img")
            stick_res = []
            for sticker in stickers:
                stick_res.append(sticker.get("title"))
            stickers = " ".join(stick_res)
        except:
            stickers = ""
        card_dict = {
            "Название": name,
            "Цена": price,
            "Стикеры": stickers,
            "Ссылка": href
        }
        result.append(card_dict)
    sleep(1)
    print(f"Page - {page}")

with open("res.json", "a", encoding='utf-8') as file:
    json.dump(result, file, indent=4, ensure_ascii=False)
