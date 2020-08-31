#!/usr/bin/env python
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


def _preprocess_data(data_dir, audio_dir, label_filter, space_after_every_character=False):
    for dataset in ['train', 'test', 'dev']:
        dataset_dir = path.join(path.abspath(data_dir), dataset)
        
        person_dir = []
        person_dir = os.listdir(dataset_dir)
        print(dataset)
        for p_dir in person_dir :
            abs_p_dir = []
            abs_p_dir = path.join(dataset_dir, p_dir)
            print(p_dir)
            files = []
            files = os.listdir(abs_p_dir)
            #print(files)
            for file in files :
                file_name = path.join(abs_p_dir, file)
                ext = os.path.splitext(file_name)[-1]
                if ext == '.flac' :
                    flac_filename = ''
                    flac_filename = path.join(abs_p_dir, file)
                    #print(flac_filename)
                    wav_filename = path.join(audio_dir, dataset, path.splitext(file)[0] + ".wav")
                    #print(wav_filename)
                    _maybe_convert_wav(flac_filename, wav_filename)

                if ext == '.txt' :
                    trans_file = path.join(abs_p_dir, file)
                    shutil.copy2(trans_file, path.join(audio_dir, dataset, file)) 

    print("*********************** wav file is made ***********************")    

    for dataset in [ 'train', 'test', 'dev']:
        print("************",   dataset, "************************")
        wav_dir = path.join(path.abspath(audio_dir), dataset)

        transcript_csv = path.join(audio_dir, dataset, dataset + ".csv")
        with open(transcript_csv, 'w', encoding='utf-8') as trans_all :
            writer = csv.DictWriter(trans_all, fieldnames=FIELDNAMES)
            writer.writeheader()

            files = []
            files = os.listdir(wav_dir)

            def is_text_file(file_name):
                ext = path.splitext(file_name)[-1]
                if ext =='.txt' :
                    return True
                else :
                    return False

            trans_files = list(filter(is_text_file, files))
            rows = []
            lock = RLock()
            wrong_rows = []
            short_rows = []
            long_rows = []

            for tfile in trans_files :
                print(tfile)
                file = path.join(path.abspath(wav_dir), tfile)
                with open(file, encoding='utf-8') as f :
                    line = f.readline()
                    while line:
                        wav_filename = path.join(path.abspath(wav_dir), line[0:12] + ".wav")
                        file_size = -1
                        frames = 0
                        if path.exists(wav_filename):
                            file_size = path.getsize(wav_filename)
                            frames = int(subprocess.check_output(['soxi', '-s', wav_filename], stderr=subprocess.STDOUT))
                        label = label_filter(line[13:])

                        with lock:
                            if file_size == -1:
                                # Excluding samples that failed upon conversion
                                pass
                            elif label is None:
                                wrong_rows.append((os.path.split(wav_filename)[-1], file_size, label))
                                pass
                                # Excluding samples that failed on label validation
                            elif int(frames/SAMPLE_RATE*1000/10/2) < len(str(label)):
                                short_rows.append((os.path.split(wav_filename)[-1], file_size, label))
                                pass
                                # Excluding samples that are too short to fit the transcript
                            elif frames/SAMPLE_RATE > MAX_SECS:
                                long_rows.append((os.path.split(wav_filename)[-1], file_size, label))
                                pass
                                # Excluding very long samples to keep a reasonable batch-size
                            else:
                                # This one is good - keep it for the target CSV
                                rows.append((os.path.split(wav_filename)[-1], file_size, label))

                        line = f.readline()
            print("wrong*******************************************\n")
            print(wrong_rows)
            print("short*******************************************\n")
            print(short_rows)
            print("long********************************************\n")
            print(long_rows)
            for filename, file_size, transcript in rows :
                writer.writerow({'wav_filename': filename, 'wav_filesize': file_size, 'transcript': transcript})



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
