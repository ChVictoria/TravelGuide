from geopy.geocoders import Nominatim
from haversine import haversine
import pandas as pd
import numpy as np
from Nonlin_compromise_sheme import Convolution


class Guide:
    def __init__(self, json_data):
        self.sights = pd.read_json(json_data, orient='columns')
        self.geolocator = Nominatim(user_agent="travelguide1")

    def check_location(self, location):
        geocode = self.geolocator.geocode(location +" Львів")
        if geocode:
            return True
        return False
    def get_sights_for_output(self, sights):
        sights = sights.copy()
        for column in sights:
            sights.at["rating", column] = str(sights.at["rating", column]) + "/5"
        if "distance" in sights.index:
            for column in sights:
                sights.at["distance", column] = str(round(sights.at["distance", column], 3)) + " км"
        if "description" in sights.index:
            pass
            sights.drop("description", inplace=True)
        return sights



    def check_sight(self, text):
        text = text.lower()
        for sight in self.sights.columns:
            words = sight.split()
            if (sight in text) or (" ".join(words[len(words)-3:]) in text):
                return sight
        return False

    def tell_about_sight(self, sight_name):
        return self.sights.at["description", sight_name]

    def get_distance(self, place1, place2):
        loc1 = self.geolocator.geocode(place1)
        loc2 = self.geolocator.geocode(place2)
        coord1 = (loc1.latitude, loc1.longitude)
        coord2 = (loc2.latitude, loc2.longitude)
        return haversine(coord1, coord2)

    def get_criteria(self):
        return self.sights.drop("description").index

    def set_distance(self, place):
        distance_row = []
        if place:
            for sight in self.sights:
                distance_row.append(self.get_distance(place + " Львів", sight + " Львів"))
            self.sights.loc["distance"] = distance_row

    def propose_to_visit(self, sights, quantity=1, prime_criterion=None):
        sights = sights.copy()
        # Preparing data for multicriteria score
        sights.drop("description", inplace=True)

        criteria_column = {"price": 'min', "rating": 'max', "distance": 'min'}
        sights['Criteria'] = criteria_column

        sights_array = sights.to_numpy()

        coeff = np.full(len(sights_array), 1)
        if prime_criterion:
            try:
                coeff[sights.index.tolist().index(prime_criterion)] = 10
            except IndexError:
                pass

        # Scoring itself
        conv = Convolution(sights_array, coeff)
        int_score = conv.integrated_score()
        try:
            smallest = sorted(int_score)[:quantity]
        except IndexError:
            smallest = sorted(int_score)[:len(int_score)]
        optimum = [np.where(conv.score == i)[0][0] for i in smallest]

        # Preparing result
        return sights.loc[:, [sights.columns[i] for i in optimum]]

    def sort_sights(self, sights, sort_criteria):
        return sights.sort_values(by=sort_criteria, axis=1)

    def find_sights(self, type_of_sights):
        result = []
        for sight in self.sights.columns:
            if (type_of_sights in sight) or (type_of_sights in self.sights.at["description", sight]):
                result.append(sight)

        return self.sights.loc[:, result]
