from bs4 import BeautifulSoup
import requests
from urllib.parse import quote
import datetime

dt = datetime.date.today()
current_year = int(dt.year)
current_month = int(dt.month)
current_day = int(dt.day)

base_url = ""