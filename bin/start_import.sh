#!/bin/bash

dst=data/Zeroth/clips
python3 bin/import_zeroth.py --filter_alphabet $dst"/alphabet.txt" data/Zeroth/raw_data --audio_dir $dst


#dst=data/Aihub/clips
#python3 bin/import_aihub2.py --filter_alphabet data/Aihub/alphabet.txt data/Aihub/raw_data --audio_dir $dst
