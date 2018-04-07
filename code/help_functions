# -*- coding: utf-8 -*-
"""
Created on Sat Apr  7 11:01:25 2018

@author: joost
"""

# approximate radius of earth in km
# https://www.distancefromto.net/ to check if calculation is correct

from math import radians, sin, cos, atan2, sqrt

def distance(loc1, loc2):
    """
    calculates the shortest distance between two latitude-longitude locations
    
    input: two tuples with lat en lon
    
    output: the distance between the two locations as an int
    """
    R = 6373.0

    lat1 = radians(loc1[0])
    lon1 = radians(loc1[1])
    lat2 = radians(loc2[0])
    lon2 = radians(loc2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return (R * c)
