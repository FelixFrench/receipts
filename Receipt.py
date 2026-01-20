# Gather data from various sources across the internet to be printed onto a receipt for some breakfast reading


from DataSources.Weather import get_day_forecast
from DataSources.Energy import get_energy_consumption
from DataSources.Word import get_word_of_the_day
from DataSources.News import get_headlines
from DataSources.Wikipedia import get_wikipedia_info
from DataSources import Secrets

# Maximum characters per line
width = 34


# ---------- Data Gathering ----------
weather = get_day_forecast(Secrets.lat_long)

energy_data = get_energy_consumption(
    Secrets.energy_api_key,
    Secrets.energy_product, Secrets.energy_tariff,
    Secrets.energy_mpan, Secrets.energy_msn)

wotd = get_word_of_the_day(34)

news_headlines = get_headlines(Secrets.newsapi_org_key, "bbc-news", width)
sport_headlines = get_headlines(Secrets.newsapi_org_key, "bbc-sport", width)

wikipedia_text = get_wikipedia_info(width)


# ---------- Printing ----------
print("\n")

print(" WEATHER ".center(width, "="))
print(weather)
print("\n")

print(" ENERGY CONSUMPTION ".center(width, "="))
print(energy_data)
print("\n")

print(" WORD OF THE DAY ".center(width, "="))
print(wotd)
print("\n")

print(" NEWS ".center(width, "="))
print(news_headlines)
print("\n")

print(" SPORTS ".center(width, "="))
print(sport_headlines)
print("\n")

print(" WIKIPEDIA ".center(width, "="))
print(wikipedia_text)
print("\n")