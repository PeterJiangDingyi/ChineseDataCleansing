#!/bin/bash

for name in `ls *.json`
do
    mv $name ${name%.json}.jsonl
done

