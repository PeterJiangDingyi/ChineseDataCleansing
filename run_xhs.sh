#!/bin/bash

ulimit -n
# U need to modify the dest_path arg as your will.
python clean.py \
    --dest_path /data/jiangdingyi/xhs/datacleansing/store/
