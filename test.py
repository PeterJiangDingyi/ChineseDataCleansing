import re
from tomark import Tomark
import numpy as np
import json

basic_info = {"中文名": "贝马约尔", "外文名": "FranzBurgmeier", "国籍": "列支敦士登", "出生日期": "1982年4月7日", "身高": "177 cm", "体重": "73 kg", "运动项目": "足球", "所属运动队": "瓦杜兹"}

markdown = Tomark.table([basic_info])



cleaned_content="[转载]温家宝1.2:将通过适当渠道参与解决欧债问题"
cleaned_content = re.sub(r'([\u4e00-\u9fa5])[.*?]',r'\1。', cleaned_content)


cleaned_content="原文地址:古代观人秘术作者:青岛城阳律师 1、头发多的人是劳碌名,心眼小。"
cleaned_content = re.sub(r'^[^\s]*\s',"",cleaned_content)




import os

def getFlist(file_dir):
    for root, dirs, files in os.walk(file_dir):
        print('root_dir:', root)
        print('files:', files)

        print("="*60)
    return files

#resDir = '/data/data_warehouse/llm/source_data/cn-kindle/'
#flist = getFlist(resDir)


import json
import gzip
input_file="/data/data_warehouse/llm/source_data/cn-mnbvc/law/judgement/20230134/1.jsonl.gz"
input_file="/data/data_warehouse/llm/source_data/cn-mnbvc/gov/20230172/XueXiQiangGuo.jsonl.gz"
input_file="/data/data_warehouse/llm/source_data/cn-mnbvc/gov/20230172/GovReport.jsonl.gz"
input_file="/data/data_warehouse/llm/source_data/cn-mnbvc/qa/20230196/wikihow/wikihow_zh.0.jsonl.gz"
'''
with gzip.open(input_file, 'rt') as f:
    for line in f:
        js_dict = json.loads(line)
        print(js_dict)
'''


a="## 薛下村乡 \n薛下村乡是中国陕西省榆林市吴堡县下辖的一个乡。\n## 行政区划 \n薛下村乡下辖以下行政区：\n薛下村、前山村、后山村、水游村、横沟村、寨山村、安家山村、大石坬村、南山上村、李家圪崂村、东王家山村、武家山村、砖窑山村、畔畔山村、李家沟村、槐树港村、枣丰树村、准则山村、续家坬村、小王家山村、薛上村、庙岔上村、南峪则村、前胡家山村、王家圪崂村、辛社窠村、后胡家山村"
#print(len(a))


def is_TablePage(text,mean_thresh=10.0,var_thresh=8.0,m=3.0):
    tokens = re.split(r'[\n、]',text)
    conlen = np.array([len(item) for item in tokens])
    print("conlen:",conlen)
    me = np.mean(conlen)
    var = np.std(conlen,ddof=1)
    print("mean:",me)
    print("var:",var)
    conlen = conlen[abs(conlen - me) < m*var]
    me = np.mean(conlen)
    var = np.std(conlen,ddof=1)
    print("mean:",me)
    print("var:",var)
    if me < mean_thresh and var < var_thresh: return True
    return False

'''for line in open("/data/data_warehouse/llm/clean_data/cn-wiki/v6/cn-wiki-sample100-v6.jsonl"):
    if line.find("风水世家") != -1:
        js_dict = json.loads(line)
        text = js_dict["content"]
        res = is_TablePage(text)
'''

import jieba
text="检测文本中是否有乱码"
text="人眼能识别的乱码在程序看来并没有想象中那么简单。针对程序来本身也是正常的字符。下面分享下一些折中的方案：方案一：对分词后的分词率进行统计从概率层面，正常的文本分词率（文本长度/分词后个数）>2，而乱码字符则接近1。具体代码如下："
text="涓囧厓锛屾厛锽勬崘鐚"
strlen = len(text)
seglen = len(jieba.lcut(text))
#print("strlen:",strlen)
#print("seglen:",seglen)
#print("ratio:",1.0*strlen/seglen)


# /data/data_warehouse/llm/source_data/cn-xhs

tokenizer_path="/data/pangwei/chinese_llama_13b_plus14/"
tokenizer_kwargs = {
        "use_fast": True,
        "revision": "productGPT"
}

from transformers import LlamaTokenizer
tokenizer = LlamaTokenizer.from_pretrained(tokenizer_path, **tokenizer_kwargs)
tokenizer.pad_token = tokenizer.eos_token

content="没有足够的💰来买这种仪器"
tokens = tokenizer.encode(content)
num_tokens = len(tokens)


from clean_headtails_from_content import CleanHeadTailsFromContent

idx = 0
clean = CleanHeadTailsFromContent("./wechat_ads_phrase.txt")
for line in open("/root/llm/source_data/cn-wechat/wx_data_981.jsonl"):
    line = line.strip()
    if len(line) < 1: continue
    js_dict = json.loads(line)
    content = js_dict["content"]

    res = clean.clean(content)
    print("oldtext:",content)
    print("newtext:",res)
    print("=="*40)
    idx += 1
    if idx > 50: break







