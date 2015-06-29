import os
import sys

filePath = sys.argv[1]
os.system("mongoimport --db gain_data --collection received_data --file %s" % filePath)
