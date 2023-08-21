import os
import json
import argparse
import chardet
from tqdm import tqdm
from os import listdir, path



def make_clean(args):
    global_file_no = 0
    global_id_no = 0

    files = sorted(listdir(args.source_path))
    

    dest_file = os.path.join(args.dest_path,"part-{:08d}.jsonl".format(global_file_no))
    if os.path.exists(dest_file): os.remove(dest_file)
    global_file_no += 1
    of = open(dest_file,'w',encoding='utf-8')

    for dir_no,file in tqdm(enumerate(files),total=len(files)):
        
        #subset_dir = subset_dir.replace(" ","\ ")
        input_file = os.path.join(args.source_path,file)
        for line in open(input_file,"r",encoding='utf-8'):
            line = line.strip()
            if len(line) < 10: continue

            js_dict = {}
            js_dict["id"] = global_id_no
            js_dict["source"] = "cn-langchao"
            js_dict["subset"] = file
            js_dict["source_id"] = ""
            global_id_no += 1

            js_dict["content"] = line

            print(json.dumps(js_dict,ensure_ascii=False),file=of)
            if of.tell() > args.max_size:
                of.close()
                dest_file = os.path.join(args.dest_path,"part-{:08d}.jsonl".format(global_file_no))
                if os.path.exists(dest_file): os.remove(dest_file)
                of = open(dest_file,'w',encoding='utf-8')
                global_file_no += 1
    of.close()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_path',
                        type=str,
                        default="/data/data_warehouse/llm/source_data/cn-langchao",
                        help='Directory containing trained actor model')
    parser.add_argument('--dest_path',
                        type=str,
                        default="/data/data_warehouse/llm/source_data/cn-langchao2",
                        help='Directory containing trained actor model')
    parser.add_argument('--dataset_name',
                        type=str,
                        default="cn-langchao",
                        help="")
    parser.add_argument('--max_size',
                        type=int,
                        default=200 * 1024 * 1024,
                        help="max chunk size")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()

    if not os.path.exists(args.dest_path):
        os.makedirs(args.dest_path, exist_ok=True)
    make_clean(args)



