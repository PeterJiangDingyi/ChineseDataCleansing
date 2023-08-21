# -*- encoding:utf-8 -*-
from flashtext import KeywordProcessor
from util import load_list_from_structedTxt

class CleanHeadTailsFromContent:
    def __init__(self, keyphrase_file):
        self.ads_wechat_flashtext = KeywordProcessor()

        ads_phrase_list = load_list_from_structedTxt(keyphrase_file)
        print(f"load {len(ads_phrase_list)} ads phrases.")
        self.ads_wechat_flashtext.add_keywords_from_list(ads_phrase_list)
        self.split_flg = ['。','\n']

    def clean(self,text):
        text = text.strip()
        text = self.forward(text)
        text = self.backward(text)
        text = text.strip()
        return text

    def forward(self,text):
        
        prev_density = 0.0
        prev_idx = 0

        tlen = len(text)
        while prev_idx < tlen:
            curr_idx = prev_idx
            while curr_idx < tlen and text[curr_idx] not in self.split_flg: curr_idx += 1

            head_text = text[prev_idx:curr_idx+1]
            if len(head_text) < 1:
                prev_idx = curr_idx + 1
                continue
            diff_cnt,keylen = self.calculate_density(head_text)
            #print(f"head_text:{head_text}, diff_cnt:{diff_cnt}, keylen:{keylen}")
            if diff_cnt < 1:
                break
            else:
                prev_idx = curr_idx + 1
        text = text[prev_idx:]
        return text

    def backward(self,text):
        last_density = 0.0
        last_idx = len(text) - 1

        while last_idx > 0:
            curr_idx = last_idx
            while curr_idx > 0 and text[curr_idx] not in self.split_flg: curr_idx -= 1

            tail_text = text[curr_idx+1:last_idx+1]
            if len(tail_text) < 1:
                last_idx = curr_idx - 1
                continue
            diff_cnt,keylen = self.calculate_density(tail_text)
            #print(f"tail_text:{tail_text}, diff_cnt:{diff_cnt}, keylen:{keylen}")
            if diff_cnt < 1:
                break
            else:
                last_idx = curr_idx
        text = text[0:last_idx+2]
        return text

    def calculate_density(self,text):
        keyword_list = self.ads_wechat_flashtext.extract_keywords(text)
        keylen = sum([len(item) for item in keyword_list])
        #ratio = 1.0*keylen / (len(text) + 0.005)
        diff_cnt = len(set(keyword_list))
        return diff_cnt,keylen


