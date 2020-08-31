#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
Broadly speaking, this script takes the audio downloaded from Common Voice
for a certain language, in addition to the *.tsv files output by CorporaCreator,
and the script formats the data and transcripts to be in a state usable by
DeepSpeech.py
Use "python3 import_cv2.py -h" for help
'''
from __future__ import absolute_import, division, print_function

# Make sure we can import stuff from util/
# This script needs to be run from the root of the DeepSpeech repository
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import csv
import sox
import argparse
import subprocess
import progressbar
import unicodedata
import shutil
import glob
import re
import pandas as pd
import numpy as np
import hgtk

from util.regex import regex_str, isdigit, isHangul, isspecialletter, isNone
from sklearn.model_selection import train_test_split
from os import path
from threading import RLock
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count
from util.downloader import SIMPLE_BAR
from util.text import Alphabet, validate_label, UTF8Alphabet
from util.feeding import secs_to_hours


FIELDNAMES = ['wav_filename', 'wav_filesize', 'transcript']
SAMPLE_RATE = 16000
MAX_SECS = 15
MIN_MILI_SECS = 17
DATASET = ['train', 'test', 'dev']

def _preprocess_data(data_dir, audio_dir, label_filter, space_after_every_character=False):
    
    data_dir_list = [ path.join(path.abspath(data_dir),a)  for a in os.listdir(data_dir) if os.path.isdir(path.join(path.abspath(data_dir),a)) ]
    print(data_dir_list)

    # Keep track of how many samples are good vs. problematic
    counter = {'all': 0, 'failed': 0, 'invalid_label': 0, 'too_short': 0, 'too_long': 0, 'total_time': 0}
    lock = RLock()
    rows = []
    rows_short = []
    rows_long = []
    rows_wrong = []

    transcript_csv = path.join(audio_dir, "total.csv")
    transcript_txt = path.join(audio_dir, "total.txt")
    with open(transcript_csv, 'w', encoding='utf-8') as trans_csv, open (transcript_txt, 'w', encoding='utf-8') as trans_txt:
        writer = csv.DictWriter(trans_csv, fieldnames=FIELDNAMES)
        writer.writeheader()

        for dir in data_dir_list:
            print(dir)
            sub_dir_list = []
            sub_dir_list = [ path.join(path.abspath(dir), a)  for a in os.listdir(dir) if os.path.isdir(path.join(path.abspath(dir),a)) ]

            for sub_dir in sub_dir_list:
                print(sub_dir)
                wav_files = [] 
                wav_files = [path.join(path.abspath(sub_dir), a) for a in os.listdir(sub_dir) if a.endswith(".wav") ]
               
                for wav_file in wav_files:
#                    print(wav_file)
#                    sys.exit()
                    txt_file = path.join( path.splitext(wav_file)[0] + ".txt")
                    #print(txt_file) 
                    #_maybe_convert_wav(pcm_file, wav_filename)
                    file_size =-1
                    file_size = path.getsize(wav_file)
                    frames = int(subprocess.check_output(['soxi', '-s', wav_file], stderr=subprocess.STDOUT))
                    with open (txt_file, encoding='ms949') as f  :
                        line_org = line = f.readline()
                        #line = line.decode('iso-8859-1').encode('utf8')
                        
                        line = regex_str(line)
                        #print(line)
                        jamo_line = hgtk.text.decompose(line)
                        #print(jamo_line)
                        jamo_line = re.sub('[ᴥ]', ' ', jamo_line)
                        jamo_line = re.sub('[\n]', ' ', jamo_line)
                        #print(jamo_line)
                        label = label_filter(jamo_line)
                        #`print(label)
#                        print(isdigit(label),":", isHangul(label),":", isspecialletter(label))
                        if not isNone(label) and isHangul(label) and not isspecialletter(label):
                            with lock:
                                if file_size == -1:
                                    # Excluding samples that failed upon conversion
                                    counter['failed'] += 1
                                elif label is None:
                                    # Excluding samples that failed on label validation
                                    rows_wrong.append((wav_file, file_size, label))
                                    counter['invalid_label'] += 1
                                elif int(frames/SAMPLE_RATE*1000/10/2) < len(str(label)):
                                    # Excluding samples that are too short to fit the transcript
                                    rows_short.append((wav_file, file_size, label))
                                    counter['too_short'] += 1
                                elif int(frames/SAMPLE_RATE*10) < MIN_MILI_SECS:
                                    # Excluding samples that are too short to fit the transcript
                                    rows_short.append((wav_file, file_size, label))
                                    counter['too_short'] += 1
                                elif frames/SAMPLE_RATE > MAX_SECS:
                                    # Excluding very long samples to keep a reasonable batch-size
                                    rows_long.append((wav_file, file_size, label))
                                    counter['too_long'] += 1
                                else:
                                    # This one is good - keep it for the target CSV
                                    rows.append((wav_file, file_size, label))
                                counter['all'] += 1
                                counter['total_time'] += frames

                        else :
                            rows_wrong.append((wav_file, file_size, label))
                            #print(wav_file, line_org) 
                            counter['invalid_label'] += 1


        for filename, file_size, transcript in rows :
            writer.writerow({'wav_filename': filename, 'wav_filesize': file_size, 'transcript': transcript})
            trans_txt.write(transcript)


        short_csv = path.join(path.abspath(audio_dir), "short.csv")
        long_csv = path.join(path.abspath(audio_dir), "long.csv")
        wrong_csv = path.join(path.abspath(audio_dir), "wrong.csv")

        with open (short_csv, mode='w', encoding='utf-8') as short_c, open (long_csv, mode='w', encoding='utf-8') as long_c, open (wrong_csv, mode='w', encoding='utf-8') as wrong_c :

            writer_short = csv.DictWriter(short_c, fieldnames=FIELDNAMES)
            writer_short.writeheader()
            writer_long = csv.DictWriter(long_c, fieldnames=FIELDNAMES)
            writer_long.writeheader()
            writer_wrong = csv.DictWriter(wrong_c, fieldnames=FIELDNAMES)
            writer_wrong.writeheader()

            for filename, file_size, transcript in rows_short :
                writer_short.writerow({'wav_filename': filename, 'wav_filesize': file_size, 'transcript': transcript})
            for filename, file_size, transcript in rows_long :
                writer_long.writerow({'wav_filename': filename, 'wav_filesize': file_size, 'transcript': transcript})
            for filename, file_size, transcript in rows_wrong :
                writer_wrong.writerow({'wav_filename': filename, 'wav_filesize': file_size, 'transcript': transcript})

            
    with open (transcript_csv, 'r', encoding='utf-8') as trans_csv:
        df = pd.read_csv(trans_csv)

        #ds = df.sample(frac=1)
        train, test = train_test_split(df, test_size = 0.1, random_state=123)
        train, dev = train_test_split(train, test_size = 0.2, random_state=123)
        
        train_csv = path.join(path.abspath(audio_dir), "train.csv")
        train.to_csv(train_csv, mode='w', index = False)
        dev_csv = path.join(path.abspath(audio_dir), "dev.csv")
        dev.to_csv(dev_csv, mode='w', index = False)
        test_csv = path.join(path.abspath(audio_dir), "test.csv")
        test.to_csv(test_csv, mode='w', index = False)

        df1 = pd.read_csv(train_csv)



def _maybe_convert_wav(mp3_filename, wav_filename):
    if not path.exists(wav_filename):
        transformer = sox.Transformer()
        transformer.convert(samplerate=SAMPLE_RATE)
        try:
            transformer.build(mp3_filename, wav_filename)
        except sox.core.SoxError:
            pass


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description='Import CommonVoice v2.0 corpora')
    PARSER.add_argument('data_dir', help='Directory containing raw data files')
    PARSER.add_argument('--audio_dir', help='Directory containing the audio clips - defaults to "<data_dir>/clips"')
    PARSER.add_argument('--filter_alphabet', help='Exclude samples with characters not in provided alphabet')
    PARSER.add_argument('--normalize', action='store_true', help='Converts diacritic characters to their base ones')
    PARSER.add_argument('--space_after_every_character', action='store_true', help='To help transcript join by white space')

    PARAMS = PARSER.parse_args()

    AUDIO_DIR = PARAMS.audio_dir if PARAMS.audio_dir else os.path.join(PARAMS.data_dir, 'clips')
    ALPHABET = Alphabet(PARAMS.filter_alphabet) if PARAMS.filter_alphabet else None

    def label_filter_fun(label):
        if PARAMS.normalize:
            label = unicodedata.normalize("NFKD", label.strip()) \
                .encode("ascii", "ignore") \
                .decode("ascii", "ignore")
        label = validate_label(label)
        if ALPHABET and label:
            try:
                ALPHABET.encode(label)
            except KeyError:
                label = None
        return label

    _preprocess_data(PARAMS.data_dir, AUDIO_DIR, label_filter_fun, PARAMS.space_after_every_character)
