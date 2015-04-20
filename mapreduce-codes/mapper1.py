#!/usr/bin/env python
###############################################################################
##
## Big Data - Final Project
## mapper1.py
## Join fares and trips and search the zipcodes using rtree
## contact: drp354@nyu.edu
##
###############################################################################

import csv,sys,os
import numpy
from matplotlib.path import Path
from rtree import index as rtree
import shapefile  
from pyproj import Proj, transform


def findNeighborhood(location, index_rtree, neighborhoods):
    match = index_rtree.intersection((location[0], location[1], location[0], location[1]))
    for a in match:
        if any(map(lambda x: x.contains_point(location), neighborhoods[a][1])):
            return a
    return -1

def readNeighborhood(shapeFilename, index_rtree, neighborhoods):
    sf = shapefile.Reader(shapeFilename)
    for sr in sf.shapeRecords():
        if sr.record[0].strip() not in ['New York', 'Staten Island', 'Queens', 'Bronx','Brooklyn']:
            continue
        paths = map(Path, numpy.split(sr.shape.points, sr.shape.parts[1:]))
        bbox = paths[0].get_extents()
        map(bbox.update_from_path, paths[1:])
        index_rtree.insert(len(neighborhoods), list(bbox.get_points()[0])+list(bbox.get_points()[1]))
        neighborhoods.append((sr.record[3], paths))
    neighborhoods.append(('UNKNOWN', None)) 

def parseInput():
    for line in sys.stdin:
        line = line.strip('\n')
        values = line.split(',')
        if len(values)>1 and values[0]!='medallion': 
            yield values

def geocode(longitude,latitude,index_rtree,neighborhoods):
    if not latitude or not longitude:
        #print("Error reading longitude/latitude")
        return -1

    #convert to projected
    inProj = Proj(init='epsg:4326')
    outProj = Proj(init='epsg:26918')
    outx,outy = transform(inProj,outProj,longitude,latitude)
    pickup_location = (outx,outy)

    resultMap = findNeighborhood(pickup_location, index_rtree, neighborhoods)
    if resultMap!=-1:
        zipcode_result = neighborhoods[resultMap][0]
        return zipcode_result
    else:
        #print("Unable to convert lat-lon: %f %f"%(float(latitude),float(longitude)))
        return -1


def main():
    index_rtree = rtree.Index()
    neighborhoods = []
    agg = {}
    readNeighborhood('../zip_codes_shp/PostalBoundary.shp', index_rtree, neighborhoods)

    for values in parseInput():
        #general trips attributes 
        medallion = values[0]      
        pickup_datetime = values[5]
        dropoff_datetime = values[6]
        passenger_count = values[7]
        trip_time_in_secs = values[8]
        trip_distance = values[9]
        
        #attributes for geocoding       
        pickup_location = (float(values[10]), float(values[11]))
        dropoff_location = (float(values[12]), float(values[13]))
        pickup_zipcode = geocode(pickup_location[0], pickup_location[1],index_rtree,neighborhoods)
        dropoff_zipcode = geocode(dropoff_location[0], dropoff_location[1],index_rtree,neighborhoods)
        if (pickup_zipcode!=-1) and (dropoff_zipcode!=-1):
            print '%s\t%s,%s,%s,%s,%s,%s,%s,%s,' % (medallion,pickup_datetime,dropoff_datetime,passenger_count,trip_time_in_secs,\
                                                    trip_distance,pickup_location,pickup_zipcode,dropoff_zipcode)

if __name__ == '__main__':
    main()