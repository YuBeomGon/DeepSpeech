import os
import sys
import csv


csv_file = sys.argv[1]
#text_file = csv_file[-4:-1] = ".txt"

text_file = csv_file.replace(".csv", ".txt")
print("csv_file :", csv_file)
print("text_file :", text_file)
with open(csv_file, 'r', encoding='utf-8') as csvfile, open(text_file, 'w', encoding='utf-8') as txt :
    cfile = csv.reader(csvfile)
    count = 0
    for name, size, trans in cfile:
        #print(line)
        txt.write(trans)
        count += 1
        if count%1000 == 0:
            print(count%1000)
