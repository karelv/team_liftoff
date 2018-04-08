  # -*- coding: utf-8 -*-
"""
Created on Sat Apr  7 11:00:02 2018

@author: joost
"""

import json
import datetime
import help_functions

n_cars = 15
ride_dict = []
available_tu_ts = {}
waiting_list = []
datum = datetime.datetime(2018, 4, 9, 0, 0, 0)
datum = int(datum.timestamp())

with open('data/ridelisttest.json') as json_data:
    ride_list = json.load(json_data)
    ride_list.sort()
    ride_list_test = ride_list

class Tu():
    _registry = []

    def __init__(self, tu_dict):
        "assumes name is string"
        self._registry.append(self)
        self.name = tu_dict['name']
        self.lat = tu_dict['lat']
        self.lon = tu_dict['lon']
        self.person_capacity = tu_dict['person_capacity']
        self.battery_state = tu_dict['battery_state']
        self.battery_capacity = tu_dict['battery_capacity']
        self.avg_km_per_kwh = tu_dict['avg_km_per_kwh']
        self.state = tu_dict['state']
        self.km_hour = tu_dict['km_hour']

    def get_name(self):
        return self.name

    def get_location(self):
        return(self.lat, self.lon)

    def get_battery_state(self):
        return self.battery_state

    def get_state(self):
        return self.state

    def get_radius(self):
        return self.battery_capacity * self.battery_state * self.avg_km_per_kwh

    def get_km_hour(self):
        return self.km_hour

    def __str__(self):
        return self.get_name() \
        + ' at lat:' + str(self.get_location()[0]) + ' and lon:' + str(self.get_location()[1])\
        +' radius left:'  + str(self.get_radius())

    def update_location(self, lat, lon):
        self.lon = lon
        self.lat = lat

    def update_state(self, state):
        self.state = state

    def update_capacity(self, capacity):
        self.capacity = capacity



class Tr():

    def __init__(self, tr_dict):
        self.start_lat = float(tr_dict['start_lat'])
        self.start_lon = float(tr_dict['start_lon'])
        self.end_lat = float(tr_dict['end_lat'])
        self.end_lon = float(tr_dict['end_lon'])
        self.request_id = tr_dict['request_id']
        self.transport_type = tr_dict['transport_type']
        self.request_time = tr_dict['request_time']
        self.factor_ride = tr_dict['factor_ride']

    def get_distance_ride(self):
        return help_functions.distance((self.start_lat, self.start_lon),(self.end_lat,self.end_lon)) * self.factor_ride

    def get_request_id(self):
        return self.request_id

    def get_request_time(self):
        return self.request_time

    def get_start_loc(self):
        return(self.start_lat, self.start_lon)

    def get_distance_to_tu(self, tu_location):
        #location of transportation unit
        return help_functions.distance((tu_location[0], tu_location[1]), (self.start_lat, self.start_lon)) * self.factor_ride

    def __str__(self):
             return 'id:' + str(self.get_request_id()) + ' requests a transport at ' \
        + str(self.request_time) +' for ' \
        + str(round(self.get_distance_ride(),3)) + " KM" \
        + ' at '+ str(self.get_start_loc())

def generate_ride(tu, tr, ride_dict, distance_tu_tr, current_ts):
    tu.update_state(4)
    waiting_time = (current_ts-tr.get_request_time())  + ((distance_tu_tr/tu.get_km_hour())*3600)
    ride_dict.append([distance_tu_tr + tr.get_distance_ride(), waiting_time])

    available_ts = int(current_ts + ((distance_tu_tr/tu.get_km_hour())*3600) + ((tr.get_distance_ride()/tu.get_km_hour())*3600))
    available_tu_ts[tu.get_name()] = [available_ts, tr.end_lat, tr.end_lon]
    del tr
    return ride_dict, available_tu_ts

def finish_ride(tu, end_lat, end_lon):
    tu.update_state(3)
    tu.update_location(end_lat, end_lon)

#input is 1 tr
def find_tu(tr):
    distance_dict = {}
    for tu in Tu._registry:
        if tu.get_state() == 3:
            distance_dict[tu.get_name()] = round(tr.get_distance_to_tu(tu.get_location()),2)
    if len(distance_dict.keys()) > 0 :
        match_tu_str = min(distance_dict, key=distance_dict.get)
        return match_tu_str, distance_dict[match_tu_str]
    else:
        return -1, -1

objs = list()
for i in range(n_cars):
    name = i

    tu_dict = {
      'name': name, 'lat': 53.21720922, 'lon': 6.575406761,
      'person_capacity': 4, 'battery_state': 0.2, 'battery_capacity': 85,
      'avg_km_per_kwh':7, 'state':3,
      'km_hour':  50
    }

    objs.append(Tu(tu_dict))

for i in range(24*60*60):
    current_ts = datum + i
    if len(ride_list_test) > 0 and current_ts >= ride_list_test[0][0]:
        # now the logic for the ride starts for selecting a transportation unit
        tr_dict = {
          'start_lat': ride_list_test[0][3],
          'start_lon': ride_list_test[0][4],
          'end_lat': ride_list_test[0][5],
          'end_lon': ride_list_test[0][6],
          'request_time': ride_list_test[0][0],
          'transport_type': 1,
          'request_id': ride_list_test[0][2],
          'factor_ride': 1.5
        }

        tr = Tr(tr_dict)
        del ride_list_test[0]
        waiting_list.append(tr)

    waiting_list2 = waiting_list.copy()
    if len(waiting_list2) > 0:
        for tr in waiting_list2:
            match_tu, distance_tu_tr = find_tu(tr)
            if match_tu != -1:
                ride_dict, available_tu_ts = generate_ride(objs[match_tu], tr, ride_dict, distance_tu_tr, current_ts)
                waiting_list.remove(tr)
            else:
                pass
            del match_tu, distance_tu_tr
    available_tu_ts2 = available_tu_ts.copy()
    for tu, ts in available_tu_ts2.items():
        if int(current_ts) >= int(ts[0]):
            finish_ride(objs[tu], ts[1], ts[2])
            available_tu_ts.pop(tu, None)



