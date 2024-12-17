import requests
import json
from datetime import datetime, timedelta

#API flixbus
def get_flixbus_data(departure_date):
    url = f"https://global.api.flixbus.com/search/service/v4/search?from_city_id=e66b26bd-758d-4c59-ad1f-eddf72800f3e&to_city_id=40deee02-8646-11e6-9066-549f350fcb0c&departure_date={departure_date}&products=%7B%22adult%22%3A1%7D&currency=EUR&locale=en&search_by=cities&include_after_midnight_rides=1&disable_distribusion_trips=0&disable_global_trips=0"
    
    # URL request
    response = requests.get(url)
    
    # Request check
    if response.status_code == 200:
        data = response.json()
        trips = data.get("trips", [])
        flixbus_plecare = []
        
        if trips:
            for trip in trips:
                results = trip.get("results", {})
                for trip_uid, trip_details in results.items():
                    departure = trip_details["departure"]["date"]
                    arrival = trip_details["arrival"]["date"]
                    price = trip_details["price"]["total_with_platform_fee"]
                    
                    # Convert EURO to RON
                    price_in_local_currency = price * 4.97
                    # Data processing
                    flixbus_plecare.append({
                        "data": departure.split("T")[0], 
                        "ora_plecare": departure.split("T")[1].split("+")[0],  
                        "ora_destinatie": arrival.split("T")[1].split("+")[0],
                        "pret": price_in_local_currency  # Price * 4.97
                    })
        
        return flixbus_plecare
    else:
        print(f"Error: {response.status_code}")
        return []

# Save data to JSON file
def save_flixbus_data_to_json(flixbus_data, filename="flixbus_plecare.json"):
    with open(filename, "w") as json_file:
        json.dump({"flixbus_plecare": flixbus_data}, json_file, indent=4)
    print(f"Datele au fost salvate în {filename}")
    print(f"-"*25)


# Date search interval
def generate_date_range(start_date, end_date):
    start = datetime.strptime(start_date, "%d.%m.%Y")
    end = datetime.strptime(end_date, "%d.%m.%Y")
    delta = timedelta(days=1)
    
    date_range = []
    current_date = start
    while current_date <= end:
        date_range.append(current_date.strftime("%d.%m.%Y"))
        current_date += delta
        
    return date_range

# Request user for start/end date
start_date = input("Introduceti data de inceput (ex: 19.12.2024 / DD.MM.YYYY): ")
end_date = input("Introduceti data de sfarsit (ex: 21.12.2024 / DD.MM.YYYY): ")

# Generate date interval
date_range = generate_date_range(start_date, end_date)

# Collect data and save to JSON
flixbus_plecare = []
for date in date_range:
    flixbus_plecare += get_flixbus_data(date)

# Save data
if flixbus_plecare:
    save_flixbus_data_to_json(flixbus_plecare)
