from datetime import datetime, timedelta
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, value, PULP_CBC_CMD
import json

# Read data from JSON
with open('flixbus_plecare.json', 'r') as f:
    flixbus_data = json.load(f)
flixbus_plecare = flixbus_data['flixbus_plecare']

# Transform DATA so it can match with airplane
for entry in flixbus_plecare:
    entry["ora_plecare"] = datetime.strptime(f"{entry['data']} {entry['ora_plecare']}", "%Y-%m-%d %H:%M:%S")
    entry["ora_destinatie"] = datetime.strptime(f"{entry['data']} {entry['ora_destinatie']}", "%Y-%m-%d %H:%M:%S")
    entry["data_datetime"] = datetime.strptime(entry['data'], "%Y-%m-%d")

# Read airplane DATA
with open('zbor.json', 'r') as f:
    avion_data = json.load(f)
avion_plecare = avion_data['avion_plecare']

# Transform DATA so it can match with bus
for entry in avion_plecare:
    entry["ora_decolare"] = datetime.strptime(f"{entry['data']} {entry['ora_decolare']}", "%Y-%m-%d %H:%M:%S")
    entry["ora_aterizare"] = datetime.strptime(f"{entry['data']} {entry['ora_aterizare']}", "%Y-%m-%d %H:%M:%S")
    entry["data_datetime"] = datetime.strptime(entry['data'], "%Y-%m-%d")

# Create optimization problem
prob_departure = LpProblem("Minimizare_Cost_Transport_Plecare", LpMinimize)

# Decision vars
zbor_vars_departure = LpVariable.dicts("Zbor", range(len(avion_plecare)), 0, 1, cat="Binary")  
bus_vars_departure = LpVariable.dicts("Bus", range(len(flixbus_plecare)), 0, 1, cat="Binary")

# Minimize total cost Function
prob_departure += lpSum(
    avion_plecare[i]["pret"] * zbor_vars_departure[i] for i in range(len(avion_plecare)) 
) + lpSum(
    flixbus_plecare[j]["pret"] * bus_vars_departure[j] for j in range(len(flixbus_plecare))
), "Cost Total"

# Constraint
prob_departure += lpSum(zbor_vars_departure[i] for i in range(len(avion_plecare))) == 1, "Selectare_un_singur_zbor" 
prob_departure += lpSum(bus_vars_departure[j] for j in range(len(flixbus_plecare))) == 1, "Selectare_un_singur_bus"

# Constraint to prevent conflicts between selected flights and buses
for j in range(len(flixbus_plecare)):
    for i in range(len(avion_plecare)):
        if avion_plecare[i]["data"] != flixbus_plecare[j]["data"] or not (avion_plecare[i]["ora_aterizare"] <= flixbus_plecare[j]["ora_plecare"] <= avion_plecare[i]["ora_aterizare"] + timedelta(hours=3)): # No longer than 3 hours 
            prob_departure += zbor_vars_departure[i] + bus_vars_departure[j] <= 1, f"Conflict_{i}_{j}"

# Solving the problem
prob_departure.solve(PULP_CBC_CMD(msg=False))

# Display solution
print("Cea mai bună opțiune pentru plecare:")
for i in range(len(avion_plecare)):
    if zbor_vars_departure[i].varValue > 0.5:
        print(f"Avion: {avion_plecare[i]['data']} {avion_plecare[i]['ora_decolare'].strftime('%H:%M')} - {avion_plecare[i]['ora_aterizare'].strftime('%H:%M')} ({avion_plecare[i]['pret']} lei)")

for j in range(len(flixbus_plecare)):
    if bus_vars_departure[j].varValue > 0.5:
        print(f"FlixBus: {flixbus_plecare[j]['data']} {flixbus_plecare[j]['ora_plecare'].strftime('%H:%M')} - {flixbus_plecare[j]['ora_destinatie'].strftime('%H:%M')} ({flixbus_plecare[j]['pret']} lei)")

print(f"Cost total: {value(prob_departure.objective)} lei")
