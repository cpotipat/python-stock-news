import requests
import html
import smtplib
import os
import unicodedata

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
STOCK_API_URL = "https://www.alphavantage.co/query"
NEWS_API_URL = "https://newsapi.org/v2/everything"
MY_EMAIL = os.environ.get("MY_EMAIL")
PASSWORD = os.environ.get("PASSWORD")
API_KEY_STOCK = os.environ.get("API_KEY_STOCK")
API_KEY_NEWS = os.environ.get("API_KEY_NEWS")


STOCK_PARAMETERS = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK,
    "apikey": API_KEY_STOCK
}

response = requests.get(STOCK_API_URL, params=STOCK_PARAMETERS)
response.raise_for_status()
stock_data = response.json()
daily_data = list(stock_data["Time Series (Daily)"].items())
before_yesterday = daily_data[0][0]

yesterday_close = daily_data[0][1]["4. close"]
before_yesterday_close = daily_data[1][1]["4. close"]

percentage_diff = round((float(yesterday_close) - float(before_yesterday_close)) / float(yesterday_close) * 100, 2)

if abs(percentage_diff) >= 3:
    symbol = None
    if percentage_diff > 0:
        symbol = "🔺"
    else:
        symbol = "🔻"

    NEWS_PARAMETERS = {
        "q": COMPANY_NAME,
        "from": before_yesterday,
        "sortBy": "publishedAt",
        "apiKey": API_KEY_NEWS
    }

    news_response = requests.get(NEWS_API_URL, params=NEWS_PARAMETERS)
    news_response.raise_for_status()

    articles = html.unescape(news_response.json()["articles"])
    three_articles = articles[:3]

    formatted_articles = [f"Headline: {item['title']}. \nBrief: {item['description']}." for item in three_articles]

    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL, password=PASSWORD)

        for articles in formatted_articles:
            content = unicodedata.normalize('NFKD', articles).encode('ascii', 'ignore')

            connection.sendmail(
                from_addr=MY_EMAIL,
                to_addrs=MY_EMAIL,
                msg=f"Subject: TSLA: {percentage_diff}%\n\n"
                    f"{content}"
            )
