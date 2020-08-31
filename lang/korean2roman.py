import os
import sys
import hgtk
import re
import argparse
import csv
from korean_alphabets import eumjul
from makeroman import kor2rom_list
#import makeroman

#FIELDNAMES = ['eumjul', 'jamo', 'roman']
FIELDNAMES = ['eumjul', 'roman']

#number = len(eumjul)
#print(number)

def isHangul(text):
    #Check the Python Version
    pyVer3 =  sys.version_info >= (3, 0)

    if pyVer3 : # for Ver 3 or later
        encText = text
    else: # for Ver 2.x
        if type(text) is not unicode:
            encText = text.decode('utf-8')
        else:
            encText = text

    hanCount = len(re.findall(u'[\u3130-\u318F\uAC00-\uD7A3]+', encText))
    return hanCount > 0


def main(data_dir):

    #data_dir = sys.argv[1]
    k2r_csv = os.path.join(data_dir, "korean2roman.csv")
    rows = []
    with open (k2r_csv, mode='w', encoding='utf-8') as c :
        writer = csv.DictWriter(c, fieldnames=FIELDNAMES)
        writer.writeheader()
        for i in eumjul:
            print(i)
            if isHangul(i) :
                jamo = []
                jamo = hgtk.letter.decompose(i)
                roman = []
                str = ""
                #print(len(jamo))
                if len(jamo) == 1 :
                    roman = [""]
                elif len(jamo) == 2 :
                    roman = ["", ""]
                elif len(jamo) == 3 :
                    roman = ["", "", ""]
                else :
                    print("Error, korean size cannot exceed 3")
                    sys.exit()
                    
                for j in range(len(jamo)) :
                    roman[j] = kor2rom_list[j][jamo[j]]
                str = "".join(roman)
                print("transform:", i, jamo, roman, len(jamo))
                rows.append((i,jamo,str))
                #writer.writerow({'eumjul':i, 'jamo':jamo, 'roman':roman})
                writer.writerow({'eumjul':i, 'roman':str})
            else :
                print(i)
                pass




if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description='Import CommonVoice v2.0 corpora')
    PARSER.add_argument('--data_dir', help='Directory containing raw data files')

    PARAMS = PARSER.parse_args()

    DATA_DIR = PARAMS.data_dir if PARAMS.data_dir else os.path.join(".", 'map')


    main(DATA_DIR)

