# -*- encoding:utf-8 -*-
from itertools import groupby
import jieba_fast as jieba 
import os
import re
from string import punctuation as en_punc
import json
import numpy as np
# import jieba
#from emoji import emojize, demojize
from flashtext import KeywordProcessor
from util import sbcCase,circleCase,bracketCase,dotCase,specialCase,load_set_from_txt

class GClean:
    def __init__(self, long_required) -> None:
        self.long_required = long_required

        #self.invalid_words_checker = KeywordProcessor()
        #keyword_list = list(set(SENSITIVE_WORDS))
        #self.processor.add_keywords_from_list(keyword_list)

    def is_long_enough(self, sentence) -> bool:
        """
            if the sentence longer than the length threshold
            threshold = minimal sentence length + 3 (<n>)
        """
        return True if len(sentence) > self.long_required else False

    @staticmethod
    def is_punc(char) -> bool:
        """
            union all CN, EN punctuations
        """
        zh_punc = '｡･ω･｡，。！？＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀-｛｜｝～｟｠｢｣､、〃《》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.'
        zh_punc = zh_punc.encode('utf-8').decode('utf-8')
        punc = set(en_punc).union(zh_punc)

        return char in punc

    @staticmethod
    def is_valid_punc_at_begin(char) -> bool:
        """
            union all CN, EN punctuations
        """
        zh_punc = '，。@！？＂＄％＆＇）＊＋，－／；＜＝＞＼］＾＿｀-｜｝～｠｣､、〃》」』】〕〗〙〛〜〞〟〰〾〿–—‘’”„…‧﹏.'
        zh_punc = zh_punc.encode('utf-8').decode('utf-8')
        _en_punc = '''@!"$%&')*+,-./;<=>?\]^_`|}~'''
        punc = set(_en_punc).union(zh_punc)

        return char in punc

    @staticmethod
    def is_valid_punc_at_last(char) -> bool:
        """
            union all CN, EN punctuations
        """
        zh_punc = '，＂＄％＆＇(（＊＋，－／；＜＝＞＠＼[＾＿｀-｜｝～｠「《『【〔〖〘〚､、〃〜〞〟〰〾〿–—‘’”„…‧﹏.'
        zh_punc = zh_punc.encode('utf-8').decode('utf-8')
        _en_punc = '''"#$%&'(*+,-./;<=>?@\[^_`|{~'''
        punc = set(_en_punc).union(zh_punc)

        return char in punc
    
    @staticmethod
    def is_digit(char) -> bool:
        return char.isdigit()

    @staticmethod
    def is_chinese(char) -> bool:
        return '\u4e00' <= char <= '\u9fa5'

    @staticmethod
    def is_english(char) -> bool:
        return ((char >= u'\u0041') and (char <= u'\u005A')) \
                or ((char >= u'\u0061') and (char <= u'\u007A'))

    @staticmethod  
    def is_emoji(char) -> bool:
        return '\uDC00' <= char <= '\uDFFF' or '\uD83C' <= char <= '\uD83E'

    @staticmethod  
    def is_n(char) -> bool:
        return char == "\n"
    
    @staticmethod  
    def is_blank(char) -> bool:
        return char == " "
    
    @staticmethod
    def clean_url(sentence) -> str:
        http = re.compile(r'http[s]?:[A-Z,a-z,0-9,\-,\.,\_,\~,\:,\/,\?,\#,\[,\],\@,\!,\$,\&,\',\(,\),\*,\+,\,,\;,(\s*),\%,\=]+')
        sentence = http.sub('', sentence)
        ftp = re.compile(r'ftp?:[A-Z,a-z,0-9,\-,\.,\_,\~,\:,\/,\?,\#,\[,\],\@,\!,\$,\&,\',\(,\),\*,\+,\,,\;,(\s*),\%,\=]+')
        sentence = ftp.sub('', sentence)
        FTP = re.compile(r'FTP?:[A-Z,a-z,0-9,\-,\.,\_,\~,\:,\/,\?,\#,\[,\],\@,\!,\$,\&,\',\(,\),\*,\+,\,,\;,(\s*),\%,\=]+')
        sentence = FTP.sub('', sentence)
        www = re.compile(r'www?[A-Z,a-z,0-9,\-,\.,\_,\~,\:,\/,\?,\#,\[,\],\@,\!,\$,\&,\',\(,\),\*,\+,\,,\;,(\s*),\%,\=]+')
        sentence = www.sub('', sentence)
        return sentence

    def clean_private(self, sentence) -> str:
        email = re.compile(r'[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z_-]+)+')
        sentence = email.sub('', sentence)

        idcard = re.compile(r'[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]')
        sentence = idcard.sub('', sentence)

        mobile = re.compile(r'((\+86)?([- ])?)?(|(13[0-9])|(14[0-9])|(15[0-9])|(17[0-9])|(18[0-9])|(19[0-9]))([- ])?\d{3}([- ])?\d{4}([- ])?\d{4}')
        sentence = mobile.sub('', sentence)

        landline = re.compile(r'(\+?( |-|\.)?\d{1,2}( |-|\.)?)?(\(?\d{3}\)?|\d{3})( |-|\.)?(\d{3}( |-|\.)?\d{4,5})')
        sentence = landline.sub('', sentence)

        bank = re.compile(r'\d{15,19}')
        sentence = bank.sub('', sentence)

        social = re.compile(r'[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}')
        sentence = social.sub('', sentence)        
        return sentence
    
    def clean_deplicate_punc(self, sentence) -> str:
        new_sentence = []
        for k, g in groupby(sentence):
            if self.is_punc(k):
                new_sentence.append(k)
            else:
                new_sentence.extend(g)
        return ''.join(new_sentence)
    
    # 重复两次以上的，长度至少为3的非数字文本只保留一次
    def delete_2repeating_long_patterns(self, sentence):
        pattern = re.compile(r'([^0-9]{3,}?)\1{1,}')
        return pattern.sub(r'\1', sentence)
    
    def clean_punct_at_begin(self, sentence) -> str:
        while len(sentence) > 0 and self.is_valid_punc_at_begin(sentence[0]):
            sentence = sentence[1:]
        return sentence

    def clean_punct_at_last(self, sentence) -> str:
        while len(sentence) > 0 and self.is_valid_punc_at_last(sentence[-1]):
            sentence = sentence[:-1]
        return sentence
    
    def clean_continueous_punc(self, sentence) -> str:
        new_sentence = ''

        punc_detect = False
        for char in sentence:
            if self.is_punc(char):
                if not punc_detect:
                    punc_detect = True
                    new_sentence += char
                else:
                    if char == '[' or '\\':
                        new_sentence += char
                    pass
            else:
                if punc_detect:
                    punc_detect = False
                    new_sentence += char
                else:
                    new_sentence += char

        return new_sentence
    

    def filter_long_sentences(self, text, min_length=5):
        # print(text)
        # 使用正则表达式将文本分割成句子，句子结束符可以是中文符号和英文符号
        # 不同于字符串的split，这里输出的list会包含切分处的字符，即。！？等。
        sentence_delimiters = re.compile(r'([。！？!?])')
        sentences = sentence_delimiters.split(text)
        
        # 合并句子并过滤掉长度小于min_length的句子
        filtered_sentences = [sentences[i] + sentences[i+1] for i in range(0, len(sentences)-1, 2) if len(sentences[i].strip() + sentences[i+1].strip()) >= min_length]
        
        # 将句子合并成一个字符串
        merged_text = ''.join(filtered_sentences)
        
        return merged_text

    def is_chinese_long_strings_without_punctuation(self, texts, max_length=64):
        # 定义正则表达式模式用于匹配标点符号
        punctuation_pattern = re.compile(r'[，。？！]')

        # 合并所有文本为一个字符串
        #combined_text = ' '.join(texts)

        # 使用正则表达式匹配标点符号
        has_punctuation = bool(punctuation_pattern.search(texts))

        # 如果文本包含标点符号，返回原始文本列表；否则，只返回长度不超过max_length的文本
        '''if has_punctuation:
            filtered_texts = ''.join([text for text in texts if len(text) <= max_length])
        else:
            filtered_texts = texts[0:max_length]

        return filtered_texts
        '''
        if has_punctuation: return True
        else: return False

    def clean_valid(self, sentence) -> str:
        new_sentence = ''
        for char in sentence:
            if char.isprintable() and  (self.is_n(char) or self.is_blank(char) or self.is_english(char) or self.is_chinese(char) or self.is_digit(char) or self.is_punc(char)):
                new_sentence += char
        return new_sentence
    
    def clean(self, sentence) -> str:
        """
            1. clean invalid words
            2. clean duplicated punctuation
            3. clean up spam words
            4. remove sentences that too short
        """
        # clean
        sentence = self.clean_valid(sentence)
        # clean url
        sentence = self.clean_url(sentence)
        return sentence
    
    def ChineseLessThan60(self, sentence) -> str:
        count = 0
        chinese_count=0
        for char in sentence:
            count+=1 
            if self.is_chinese(char):
                chinese_count += 1            
        if chinese_count/count >= 0.6:
            return sentence
        else:
            return False

    def deleteSpaceBetweenChinese(self, sentence):
        pattern = re.compile(r'([\u4e00-\u9fa5|\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\|])[\s\t]+')
        cleaned = pattern.sub(r'\1', sentence)
        pattern = re.compile(r'[\s\t]+([\u4e00-\u9fa5|\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\|])')
        return pattern.sub(r'\1', cleaned)

    def is_having_sentive_words(self, text, keywords, threshold=3):
        keyword_count = {}
        for keyword in keywords:
            keyword_count[keyword] = text.count(keyword)
        total_count = sum(keyword_count.values())
        if total_count < threshold:
            return False
        return True

    def clean_script(self, text):
        # 清理script
        script = re.compile(r'<.*?>')
        cleaned_text = script.sub('', text)
        return cleaned_text

    def is_TablePage(self,text,mean_thresh=10.0,var_thresh=8.0,m=3.0):
        sp = re.compile(r'[\n、]')
        tokens = sp.split(text)
        tokens = tokens[::2]
        if len(tokens) < 2: return False
        conlen = np.array([len(item) for item in tokens])
        me = np.mean(conlen)
        var = np.std(conlen,ddof=1)
        conlen = conlen[abs(conlen - me) < m*var]
        me = np.mean(conlen)
        var = np.std(conlen,ddof=1)
        if me < mean_thresh and var < var_thresh: return True
        return False

    # 2023-08-14~08-19, 检测文本中是否有乱码,
    # 统计分词后的分词率
    def is_having_chaoswords_1(self,text):
        strlen = len(text)
        seglen = len(jieba.lcut(text))
        if strlen / seglen < 1.1:
            return True,"having_chaoswords:strlen:{},seglen:{}".format(strlen,seglen)
        else:
            return False,""
    # 是否包含生僻字
    def is_having_chaoswords_2(self,text):
        try:
            text.encode("gb2312")
        except UnicodeEncodeError:
            return True
        return False

    def text_normalization(self,text):
        text = sbcCase(text) # 全角转半角
        text = circleCase(text) # 特殊字符
        text = bracketCase(text) # 特殊字符
        text = dotCase(text) # 特殊字符
        text = specialCase(text) # 特殊字符
        return text
    # 2023-08-17, 清楚重复和连续字符时保留Markdown的表格
    def clean_duplicate_punc_excludeMD(self, sentence) -> str:
        new_sentence = []
        for k, g in groupby(sentence):
            if self.is_punc(k) and (k not in ['-','#']):
                new_sentence.append(k)
            else:
                new_sentence.extend(g)
        return ''.join(new_sentence)

    def clean_continueous_punc_excludeMD(self, sentence) -> str:
        new_sentence = ''
        punc_detect = False
        for char in sentence:
            if self.is_punc(char)  and (char not in ['-','#','|']):
                if not punc_detect:
                    punc_detect = True
                    new_sentence += char
                else:
                    if char == '[' or '\\':
                        new_sentence += char
                    pass
            else:
                if punc_detect:
                    punc_detect = False
                    new_sentence += char
                else:
                    new_sentence += char

        return new_sentence

    def remove_text_after_at(self,text):
        # 使用正则表达式匹配从 "@" 开始到第一个终止符号之间的内容
        pattern = re.compile(r'@.*?[\s,;。,，；。！？]')
        new_text = pattern.sub('', text)
        return new_text

    def clean_dashes(self, text):
        # 清理多余的-，常见于markdown表格
        pattern = re.compile(r'-{4,}')
        cleaned_text = pattern.sub('---', text)
        return cleaned_text

