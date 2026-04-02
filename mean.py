import numpy

stat = []
import csv

with open("res.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        stat.append(float(row["Timestamp (ns)"]))
print(len(stat))
print(numpy.mean(stat))
