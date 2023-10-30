from geopy.geocoders import Nominatim
from haversine import haversine
import pandas as pd
import numpy as np
from Nonlin_compromise_sheme import Convolution


class Guide:
    def __init__(self, json_data):
        self.sights = pd.read_json(json_data, orient='columns')
        self.geolocator = Nominatim(user_agent="travelguide1")

    def check_sight(self, text):
        for sight in self.sights.columns:
            if sight in text:
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

    def set_distance(self, place):
        distance_row = ["distance"]
        if place:
            for sight in self.sights:
                distance_row.append(self.get_distance(place, sight))
            self.sights = pd.concat([self.sights, pd.DataFrame([distance_row])])

    def propose_to_visit(self, sights, quantity=1, prime_criterion=None):
        # Preparing data for multicriteria score
        sights.drop("description", inplace=True)


        criteria_column = {"price": 'min', "rating": 'max', "distance":'min'}
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
        return sights.loc[:, [sights.columns(i) for i in optimum]]

    def sort_sights(self, sights, sort_criteria):
        return sights.sort_values(by=sort_criteria)

    def find_sights(self, type):
        result = []
        for sight in self.sights.columns:
            if type in sight or type in self.sights[sight]['description']:
                result.append(sight)

        return self.sights.loc[:, result]


