#!/bin/bash
#data="data/KO/aihub"
dst="data/Zeroth/clips"
file=$1
BATCH_SIZE=32


EPOCH=140
LEARN_RATE=0.00005

#./DeepSpeech.py --train_files $dst"/train.csv" --dev_files $dst"/dev.csv" --test_files $dst"/test.csv" --automatic_mixed_precision=True --checkpoint_dir data/Zeroth/check_point/ckpt1 --export_dir $dst"/export" --train_batch_size $BATCH_SIZE --dev_batch_size $BATCH_SIZE --test_batch_size $BATCH_SIZE --summary_dir $dst"/summary" --epochs $EPOCH --alphabet_config_path $dst"/alphabet.txt" --learning_rate $LEARN_RATE

./DeepSpeech.py --train_files data/Zeroth/test.csv --dev_files $dst"/dev.csv" --test_files $dst"/test.csv" --automatic_mixed_precision=True --checkpoint_dir data/Zeroth/check_point/ckpt1 --export_dir $dst"/export" --train_batch_size 2 --dev_batch_size $BATCH_SIZE --test_batch_size $BATCH_SIZE --summary_dir $dst"/summary" --epochs $EPOCH --alphabet_config_path $dst"/alphabet.txt" --learning_rate $LEARN_RATE



#data="data/Aihub"
#dst=$data"/clips"
#file=$1
#BATCH_SIZE=32
#
#
#EPOCH=140
#LEARN_RATE=0.0002
#
#./DeepSpeech.py --train_files $dst"/train.csv" --dev_files $dst"/dev.csv" --test_files $dst"/test.csv" --automatic_mixed_precision=True --checkpoint_dir $data"/checkpoint/ckpt1" --export_dir $data"/export" --train_batch_size $BATCH_SIZE --dev_batch_size 32 --test_batch_size $BATCH_SIZE --summary_dir $data"/summary" --epochs $EPOCH --alphabet_config_path $data"/alphabet.txt" --learning_rate $LEARN_RATE
#
#
#EPOCH=140
#LEARN_RATE=0.00004
#
#./DeepSpeech.py --train_files $dst"/train.csv" --dev_files $dst"/dev.csv" --test_files $dst"/test.csv" --automatic_mixed_precision=True --checkpoint_dir $data"/checkpoint/ckpt1" --export_dir $data"/export" --train_batch_size $BATCH_SIZE --dev_batch_size 32 --test_batch_size $BATCH_SIZE --summary_dir $data"/summary" --epochs $EPOCH --alphabet_config_path $data"/alphabet.txt" --learning_rate $LEARN_RATE
#
#
#EPOCH=140
#LEARN_RATE=0.000008
#
#./DeepSpeech.py --train_files $dst"/train.csv" --dev_files $dst"/dev.csv" --test_files $dst"/test.csv" --automatic_mixed_precision=True --checkpoint_dir $data"/checkpoint/ckpt1" --export_dir $data"/export" --train_batch_size $BATCH_SIZE --dev_batch_size 32 --test_batch_size $BATCH_SIZE --summary_dir $data"/summary" --epochs $EPOCH --alphabet_config_path $data"/alphabet.txt" --learning_rate $LEARN_RATE
#
#
#EPOCH=140
#LEARN_RATE=0.000001
#
#./DeepSpeech.py --train_files $dst"/train.csv" --dev_files $dst"/dev.csv" --test_files $dst"/test.csv" --automatic_mixed_precision=True --checkpoint_dir $data"/checkpoint/ckpt1" --export_dir $data"/export" --train_batch_size $BATCH_SIZE --dev_batch_size 32 --test_batch_size $BATCH_SIZE --summary_dir $data"/summary" --epochs $EPOCH --alphabet_config_path $data"/alphabet.txt" --learning_rate $LEARN_RATE
