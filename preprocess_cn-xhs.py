# -*- encoding:utf-8 -*-
import os
import json
import multiprocessing as mp
import re
from tqdm import tqdm
import argparse
from os import listdir, path
from general_policy import GClean
from read_xhs_note_data import read_data, read_excel
from tqdm import tqdm
import regex as re
from emoji import emojize, demojize
import multiprocessing as mp
from emoji import emojize, demojize

KEYS = [
    'like_count',
    'collect_count',
    'share_count',
    'comment_count'
]

XHS_SQL = read_data()

LONG_REQUIRED = 50
VAL_FILETR = 50
PROCESS = 16

cleaner = GClean(LONG_REQUIRED)

def val_pro(val):
    if val == 'null' or val is None:
        return 0
    else:
        return int(val)

def jobj2clean(jobj):
    """
        mp process controller
    """
    for itm in tqdm(jobj):
        yield itm

def controller(input_file):
    yield (input_file['note_id'], input_file, 'xhs')

def step1(text):
    global KEYS
    count = 0
    for key in KEYS:
        count += val_pro(text[key])

    if len(text['content']) < LONG_REQUIRED or count <= VAL_FILETR:
        return "step1", 0, text['content']
    
    # g0 CleanScript
    cleaned_content = cleaner.clean_script(demojize(text['content']))
    # g4 CleanDuplicatedPunctuation
    cleaned_content = cleaner.clean_deplicate_punc(cleaned_content)

    # g1 InvalidWords + g22 ChineseLessThan60
    cleaned_content = cleaner.clean_valid(cleaned_content)

    # g2 CleanPunctuationsAtHeadTail
    cleaned_content = cleaner.clean_punct_at_last(cleaned_content)
    cleaned_content = cleaner.clean_punct_at_begin(cleaned_content)

    # g3 EngPeriod2ChinPeriod
    cleaned_content = re.sub('\\[.*?]', '。', cleaned_content)

    # g5 FanTi2Simplify
    cleaned_content = re.sub('「', '“', cleaned_content)
    cleaned_content = re.sub('」', '”', cleaned_content)
    cleaned_content = re.sub('【', '[', cleaned_content)
    cleaned_content = re.sub('】', ']', cleaned_content)

    # g16 CleanPersonInfoDoc
    cleaned_content = cleaner.clean_private(cleaned_content)

    # g6 CleanURL
    cleaned_content = cleaner.clean_url(cleaned_content)

    # g7 CleanContinueousPuncs
    cleaned_content = cleaner.clean_continueous_punc(cleaned_content)

    # g10 CleanDuplicationInText
    cleaned_content = cleaner.delete_2repeating_long_patterns(cleaned_content)

    # g13 TooShortSentence
    cleaned_content = cleaner.filter_long_sentences(cleaned_content)
    
    # g20 TooLongSentence
    cleaned_content = cleaner.remove_long_strings_without_punctuation(cleaned_content)
    
    # g24 LongEnough
    if len(cleaned_content) >= LONG_REQUIRED:
        return "step1",1, emojize(cleaned_content)
    return "step1", 0, emojize(cleaned_content)

def step2(text):
    # ["politician","badword","gumble","sex","ads","dirty"]
    is_sentive,key_words = BadChecker.is_spam_text(text,
        thresh_hold=3,
        black_dataType=["badword","gumble","sex","ads","dirty"]
    )
    if is_sentive:
        return "has_sensitive_words:{}".format(key_words),0,text

    return "",1,text


def step3():
    pass

def make_clean(items):
    line_no,line,input_file = items

    clean_policy = ""
    clean_status = 0

    # step 1: text normalization
    clean_policy,clean_status,text = step1(line)
    if clean_status == 1:
        # step 2: low quality
        clean_policy,clean_status,text = step2(text)
        #if clean_status == 1:
        #    # step 3: text duplication
        #    clean_policy,clean_status,text = step3(text)
    
    return {
        "id":line_no,
        "source_id":"",
        "source":"xhs",
        "subset":"{}".format(os.path.basename(input_file)),
        "clean_policy":"{}".format(clean_policy if clean_status == 0 else ""),
        "clean_status":clean_status,
        "content":text,
    }

def HandleSingleFile(input_file, good_fo, bad_fo):
    pools = mp.Pool(PROCESS)

    flush_steps = 0
    flush_per_steps = 1000
    for res in pools.imap(make_clean, controller(input_file)):
        if res is not None:
            jstr = json.dumps(res, ensure_ascii=False)
            if res["clean_status"] == 1:
                good_fo.write(jstr+"\n")
            else:
                bad_fo.write(jstr+"\n")
            flush_steps += 1
            if flush_steps % flush_per_steps == 0:
                good_fo.flush()
                bad_fo.flush()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_path',
                        type=str,
                        default="/hpc_data/pangwei/yuan1.0/open_source_1T",
                        help='Directory containing trained actor model')
    parser.add_argument('--dest_path',
                        type=str,
                        default="/hpc_data/data_warehouse/llm/source_data/cn-xhs",
                        help='Directory containing trained actor model')

    parser.add_argument('--max_size',
                        type=int,
                        default=200 * 1024 * 1024,
                        help="max chunk size")

    args = parser.parse_args()
    return args

def get_data(date_list):
    data = []
    for date in tqdm(date_list):
        if hasattr(data, '__iter__'):
            data.extend(XHS_SQL.get_xhs_note(date=date))

    return data

if __name__ == '__main__':
    #file = "小红书日期统计.xlsx"
    file = "./xhs_date.xlsx"
    oper = read_excel()
    res = oper.excel_read(file_name=file)

    # <=2020, 2021, 2022, 2023
    date_list = [[], [], [], []]
    c_bf_clean = [0, 0, 0, 0]
    c_af_clean = [0, 0, 0, 0]

    for itm in res:
        _year = int(itm['dt'].split('-')[0]) - 2020
        if _year < 0:_year = 0
        date_list[_year].append(itm['dt'])
        c_bf_clean[_year] += itm['note_count']

    args = parse_args()

    if not os.path.exists(args.dest_path):
        os.makedirs(args.dest_path, exist_ok=True)

    global_file_no = 0
    good_output_file = os.path.join(args.dest_path,"part-{:06d}.jsonl".format(global_file_no))
    if os.path.exists(good_output_file): os.remove(good_output_file)
    good_fo = open(good_output_file,'w',encoding='utf-8')

    for i in range(0, 4, 1):
        print(f'{2020+i}: {c_bf_clean[i]}')

        print('Get data: ', end='')
        data = get_data(date_list[i][:1])
        # print("dataType:",type(data))
        for i in tqdm(data):
            tmp = json.dumps(i,ensure_ascii=False)
            good_fo.write(tmp+"\n")
        if good_fo.tell() > args.max_size:
            good_fo.close()
            dest_file = os.path.join(args.dest_path,"part-{:06d}.jsonl".format(global_file_no))
            if os.path.exists(dest_file): os.remove(dest_file)
            good_fo = open(dest_file,'w',encoding='utf-8')
            global_file_no += 1
    good_fo.close()

