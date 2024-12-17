from subprocess import call, sys
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions
from bs4 import BeautifulSoup
import datetime
import json
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

def airline():

    origin = "TSR.AIRPORT"
    destination = "BGY.AIRPORT"
    
    # Request date from user
    day = int(input("Introduceți ziua (ex: 19): "))
    month = int(input("Introduceți luna (ex: 12): "))
    year = int(input("Introduceți anul (ex: 2024): "))

    # Start date
    startdate = datetime.date(year, month, day)
    
    # Search for flights 4 days from the start date,if start date is 19 dec, search until 22 dec)
    interval_days = 4
    flight_data_list = []  # flights list 

    for i in range(interval_days):
        current_day = startdate + datetime.timedelta(days=i)
        startdate_str = current_day.strftime("%Y-%m-%d")
        
        # SEARCH URL
        url = f"https://flights.booking.com/flights/{origin}-{destination}/?type=ONEWAY&adults=1&cabinClass=ECONOMY&children=&from={origin}&to={destination}&fromCountry=RO&toCountry=IT&fromLocationName=Aeroportul+Interna%C5%A3ional+Traian+Vuia+Timi%C8%99oara&toLocationName=Aeroportul+Interna%C8%9Bional+Orio+Al+Serio+Milano&depart={startdate_str}&sort=BEST&travelPurpose=leisure&aid=2430892&label=flights-booking-unknown&ext-tr=AI7DpqIcdGDOquSfhDD8b32bqNuAabHm-_46xJuCNbFS6HZQIfWchFw%3D%3D"
        
        # Chrome Driver . exe
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Rulează Chrome în mod headless (fără interfață grafică)
        chrome_options.add_argument("--disable-gpu")  # Dezactivează GPU
        chrome_options.add_argument("--no-sandbox")  # Dezactivează sandboxing-ul (important pentru Colab)
        chrome_options.add_argument("--disable-dev-shm-usage")  # Probleme de memorie partajată
        chrome_options.add_argument("--remote-debugging-port=9222")  # Setează portul de debugging
        chrome_options.binary_location = '/usr/bin/chromium-browser'


        # When run, hide the browser
        chrome_options.add_argument("--headless")

        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(20)
        driver.get(url)

        time.sleep(5)
        # Web Scraping
        soup = BeautifulSoup(driver.page_source, 'lxml')

        # Extracting departure, arrival times and price from website, those are classes from the website where the data is showed
        departure_time = soup.find('div', {'data-testid': 'flight_card_segment_departure_time_0'}).getText() if soup.find('div', {'data-testid': 'flight_card_segment_departure_time_0'}) else "N/A"
        arrival_time = soup.find('div', {'data-testid': 'flight_card_segment_destination_time_0'}).getText() if soup.find('div', {'data-testid': 'flight_card_segment_destination_time_0'}) else "N/A"
        price = soup.find('div', {'class': 'FlightCardPrice-module__priceContainer___nXXv2'}).getText() if soup.find('div', {'class': 'FlightCardPrice-module__priceContainer___nXXv2'}) else "N/A"

        # add :00 at the end so it match the time format
        departure_time = f"{departure_time}:00" if departure_time != "N/A" else "N/A"
        arrival_time = f"{arrival_time}:00" if arrival_time != "N/A" else "N/A"
        
        # check if price is a word/ letter then transform
        try:
            price = float(price.replace('RON', '').replace('€', '').strip())
        except ValueError:
            price = 0.0 

        # data structure
        flight_data = {
            "data": startdate_str,
            "ora_decolare": departure_time,
            "ora_aterizare": arrival_time,
            "pret": price * 4.97
        }

        #   print the data before saving it
        print(f"-"*25)
        print("Informații despre plecarea avionului:")
        print(f"Data plecării: {flight_data['data']}")
        print(f"Ora de decolare: {flight_data['ora_decolare']}")
        print(f"Ora de aterizare: {flight_data['ora_aterizare']}")
        print(f"Preț (RON): {flight_data['pret']:.2f}")
        print(f"-"*25)

        # Add date to list
        flight_data_list.append(flight_data)

        time.sleep(5)
        driver.quit()

    # Save flight data to JSON file
    flight_json = {
        "avion_plecare": flight_data_list
    }

    with open('zbor.json', 'w', encoding='utf-8') as json_file:
        json.dump(flight_json, json_file, ensure_ascii=False, indent=4)

    return "success"

airline()
