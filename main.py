import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
from env import password_email, email_login, d_morgun, b_romanenko

url = "https://www.avito.ru/rostov-na-donu/kvartiry/sdam/na_dlitelnyy_srok/1-komnatnye-ASgBAQICAkSSA8gQ8AeQUgFAzAgUjlk?cd=1&district=349&pmax=14100&s=104"



def get_kvartir():
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    a = soup.select("div.iva-item-body-NPl6W")
    for i in range(len(a)):
        item_title = a[i].select(".iva-item-titleStep-2bjuh > a")[0].attrs["title"]
        item_href = "https://www.avito.ru" + a[i].select(".iva-item-titleStep-2bjuh > a")[0].attrs["href"]
        item_price = a[i].select(".iva-item-priceStep-2qRpg > span > span > meta[itemprop='price']")[0].attrs["content"]
        item_address = a[i].select(".geo-address-9QndR > span")[0].string
        item_data = str(datetime.now().strftime("%Y-%m-%d-%H:%M ")) + a[i].select(".iva-item-dateInfoStep-2xJEa")[0].select("div[data-marker='item-date']")[0].string
        if check_in_table(item_href):
            continue
        else:
            pandas_exel(item_title, item_address, item_price, item_data, item_href)
            print(item_title)
            print(item_address)
            print(item_price)
            print(item_data)
            print(item_href)
            send_mes(item_title, item_address, item_price, item_data, item_href)


def check_in_table(href):
    file = pd.read_excel("kvartir.xlsx", usecols=['Название', 'Адрес', 'Цена', 'Время', 'Ссылка'],
                         header=0)  # header (None, если отстутствует заголовок)
    hr = file["Ссылка"].tolist()
    if href in hr:
        return True
    return False


def pandas_exel(item_title, item_address, item_price, item_data, item_href):
    file = pd.read_excel("kvartir.xlsx", usecols=['Название', 'Адрес', 'Цена', 'Время', 'Ссылка'],
                         header=0)  # header (None, если отстутствует заголовок)
    headers = file.columns.ravel()
    title = file["Название"].tolist()  # Перевести столбец в список
    addrs = file["Адрес"].tolist()  # Перевести столбец в список
    prise = file["Цена"].tolist()  # Перевести столбец в список
    time = file["Время"].tolist()  # Перевести столбец в список
    href = file["Ссылка"].tolist()
    title.append(item_title)
    addrs.append(item_address)
    prise.append(item_price)
    time.append(item_data)
    href.append(item_href)
    print("")
    df = pd.DataFrame({
        headers[0]: title,
        headers[1]: addrs,
        headers[2]: prise,
        headers[3]: time,
        headers[4]: href
    })
    df.to_excel("kvartir.xlsx")


def send_mes(item_title, item_address, item_price, item_data, item_href):
    import smtplib  # Импортируем библиотеку по работе с SMTP

    # Добавляем необходимые подклассы - MIME-типы
    from email.mime.multipart import MIMEMultipart  # Многокомпонентный объект
    from email.mime.text import MIMEText  # Текст/HTML
    from email.mime.image import MIMEImage  # Изображения

    server = 'smtp.mail.ru'
    user = email_login
    password = password_email

    recipients = [email_login, b_romanenko, d_morgun]
    sender = email_login
    subject = 'Квартира'
    text = item_title + "\n" + item_address + "\n" + item_price + "\n" + item_data + "\n" + item_href

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = 'Python script <' + sender + '>'
    msg['To'] = ', '.join(recipients)
    msg['Reply-To'] = sender
    msg['Return-Path'] = sender

    part_text = MIMEText(text, 'plain')

    msg.attach(part_text)

    mail = smtplib.SMTP_SSL(server)
    mail.login(user, password)
    mail.sendmail(sender, recipients, msg.as_string())
    mail.quit()


while True:
    get_kvartir()
    time.sleep(5 * 60)

