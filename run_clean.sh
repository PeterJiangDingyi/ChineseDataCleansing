#!/bin/bash

dataset="cn-wechat1"
clearning_version="v2"

source_dir="/root/llm/source_data/${dataset}"
dest_dir="/root/llm/clean_data/${dataset}/${clearning_version}"

# Step1: Perform dataset cleaning
python wechat_clean.py \
    --num_workers 16 \
    --dataset_name ${dataset} \
    --source_path ${source_dir} \
    --dest_path ${dest_dir}
if [ $? -ne 0 ]; then
    echo "clean.py failed."
    exit
else
    echo "clean.py succeed."
fi

<<EOF
# Step2: depupli amoung texts 
python text-dedup/text_dedup/minhash.py \
    --path ${source_dir} \
    --name ${dataset} \
    --output ${dest_dir} \
    --column content
EOF

# Step2: Make tokenizing with Frontis-LLaMA-13B, to yield ${dataset}-meta-info.json
tokenizer_path="/data/pangwei/chinese_llama_13b_plus14/"
python tokenizer.py \
    --dataset_name ${dataset} \
    --dataset_path ${dest_dir}/good \
    --output_path ${dest_dir} \
    --tokenizer_path ${tokenizer_path} \
    --version ${clearning_version}
if [ $? -ne 0 ]; then
    echo "tokenizer.py failed."
    exit
else
    echo "tokenizer.py succeed."
fi

# Step3: Sample 100 datas for evaluation, to produce ${dataset}-sample100.jsonl
python random_sample.py \
    --dataset_name ${dataset} \
    --dataset_path ${dest_dir}/good \
    --output_path ${dest_dir} \
    --number_sample 100 \
    --version ${clearning_version}
if [ $? -ne 0 ]; then
    echo "random_sample.py failed."
    exit
else
    echo "random_sample.py succeed."
fi

