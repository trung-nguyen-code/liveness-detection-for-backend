#!/bin/sh

python3 up_wandb.py --model-name 'sunglasses' --model-version '1'  \
--model-path 'gs://mek_models/PRODUCTION/sunglasses/1' --test-set 'FACES_CLASSIFIED_224'
