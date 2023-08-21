import re

def count_keywords_in_text(text, keywords):
    keyword_count = 0
    for keyword in keywords:
        keyword_count += len(re.findall(keyword, text))
    return keyword_count

def remove_strings_with_keywords(texts, keywords, threshold=3):
    filtered_texts = []
    for text in texts:
        keyword_count = count_keywords_in_text(text, keywords)
        if keyword_count < threshold:
            filtered_texts.append(text)
    return filtered_texts

# 测试
key_list = ["关键词1", "关键词2", "关键词3"]  # 在这里添加你的指定中文词语列表
input_texts = [
    "这是一段包含关键词1的测试文本，关键词1出现了四次，这个文本将会被删除。关键词1, 关键词1",
    "这是另一段测试文本，其中关键词2出现了两次，不会被删除。关键词2",
    "第三段文本，关键词3出现了三次，这个文本会被删除。关键词3.关键词3",
    "最后一段文本没有关键词，不会被删除。",
]

# 删除包含指定中文词语个数大于等于3的文本
filtered_texts = remove_strings_with_keywords(input_texts, key_list, threshold=3)

# 输出结果
for text in filtered_texts:
    print(text)