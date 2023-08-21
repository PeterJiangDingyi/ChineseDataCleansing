import re
import json

def delete_repeating_patterns(string):
    pattern = r'(.*?)\1{5,}'
    return re.sub(pattern, '', string, flags=re.DOTALL)

def generate(in_text):
    content = delete_repeating_patterns(in_text['chat_output'])
    if len(content) < 30:
        return
    
    gene_itm = {
            'source_id': in_text['item_id'],
            'source': "GPT_xiaohongshu", 
            'subset': in_text['subset'],
            'content': in_text['chat_input'] + content
    }

    with open('output.json', 'a', encoding='utf-8') as f:
        json.dump(gene_itm, f, ensure_ascii=False, indent=4)
    return gene_itm

if "__name__" == "__main__":
    with open('GPT_xiaohongshu.json', 'r') as json_file:
        data = json.load(json_file)

    for i in data:
        print(i)