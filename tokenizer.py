# -*- coding:utf-8 -*-
import os
import glob
import json
import argparse
from tqdm import tqdm
import multiprocessing as mp
from transformers import LlamaTokenizer

PROCESS = 64

def jobj2count(jobj):
    """
        mp process controller
    """
    for itm in tqdm(jobj):
        yield itm

def process_file(js):
    num_tokens = 0
    tokens = tokenizer.encode(js['content'])
    num_tokens += len(tokens)

    return {'num_tokens': num_tokens}


def llama_tokenizer(input_dir):
    files = sorted(glob.glob(os.path.join(input_dir, "*.jsonl"), recursive=True))

    pool = mp.Pool(PROCESS)
    total_tokens = 0

    records = {}
    records["files"] = []

    for file in files:
        tokens = 0
        filename = os.path.basename(file)#.replace(".jsonl","")
        print(f"process file: {filename}")
        with open(file,"r",encoding='utf-8') as f:
            line_content = [json.loads(line) for line in f.readlines()]
            for res in pool.imap(process_file, jobj2count(line_content)):
                tokens += res['num_tokens']
            print(f'file {filename} has {tokens} tokens.')
            records["files"].append(
                {
                    "filename":filename,
                    "llama_tokens":tokens
                }
            )
        total_tokens += tokens
    records["total_llama_tokens"] = total_tokens
    return records

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_name',
                        type=str,
                        default="jdItem",
                        help='dataset name')
    parser.add_argument('--dataset_path',
                        type=str,
                        default="/hpc_data/data_warehouse/llm/source_data/JDItem_pattern_dataset/SampledRawDataset/",
                        help='source path')
    parser.add_argument('--output_path',
                        type=str,
                        default="/hpc_data/data_warehouse/llm/source_data/JDItem_pattern_dataset/",
                        help='source path')

    parser.add_argument('--tokenizer_path',
                        type=str,
                        default="/hpc_data/pangwei/chinese_llama_13b_plus84",
                        help="tokenizer path, default LLaMA tokenizer")
    parser.add_argument('--version',
                        type=str,
                        default="v1",
                        help=""
    )
    args = parser.parse_args()
    return args

if __name__ == '__main__':

    tokenizer_kwargs = {
        "use_fast": True,
        "revision": "productGPT"
    }

    args = parse_args()
    records = {}

    tokenizer = LlamaTokenizer.from_pretrained(args.tokenizer_path, **tokenizer_kwargs)
    tokenizer.pad_token = tokenizer.eos_token

    print(f"num of llama tokens: {tokenizer.vocab_size}")

    records = llama_tokenizer(
        input_dir=args.dataset_path
    )
    records['dataset'] = args.dataset_name

    output_file = os.path.join(args.output_path,"{}-meta-info-{}.json".format(args.dataset_name,args.version))
    if os.path.exists(output_file): os.remove(output_file)
    with open(output_file, 'w') as f:
        json.dump(records, f, indent=4)
