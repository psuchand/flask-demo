from geojson import Feature, Polygon, FeatureCollection
import pandas as pd
import numpy as np
import sys

TRAINING_DIR = "./training/"
output_file = TRAINING_DIR + "nyc_sectors.json"

def make_shapefile_from_sectors(num_digits, rides):
    centers = list(set(rides.pos.values))
    
    def shape_for_center(center, num_digits):
        """
        The given center is a string, return the array of floats that defines
        the corresponding square on the map.
        """
        epsilon = 10**(-num_digits)
        shift = np.array([[0,0], [0,epsilon], [epsilon,epsilon], [epsilon,0]])

        center = np.array([float(z) for z in center.replace("(","").replace(")","").split(",")])
        return [ list(s + center) for s in shift]

    features = []
    for center in centers:
        features.append(Feature(geometry=Polygon([shape_for_center(center,num_digits)]),id=center))
        print ".",
        sys.stdout.flush()

    
    json = FeatureCollection(features).__str__()
    
    output = open(output_file, "w")
    output.write(json)
    output.close()

if __name__ == "__main__":
	
	#Read the rides list
	print "Reading data...",
	rides = pd.read_csv(TRAINING_DIR + "rides.csv", index_col =0)
	print "done."
	print "Making shapefile...",
	make_shapefile_from_sectors(2,rides)
	print "done."