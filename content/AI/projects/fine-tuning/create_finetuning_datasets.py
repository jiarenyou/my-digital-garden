import json
import pandas as pd
import random
import string
from tqdm import tqdm

# --- Configuration ---
# 用户需要将从Kaggle下载的JSON文件放在此脚本旁边
# 文件名通常是 'arxiv-metadata-oai-snapshot.json'
SOURCE_FILE = 'arxiv-metadata-oai-snapshot.json'
PRETRAIN_OUTPUT_FILE = 'pretrain_dataset.jsonl'
FINETUNE_OUTPUT_FILE = 'finetune_dataset.jsonl'
TOTAL_SAMPLES_TO_PROCESS = 4000  # 需要处理的总样本数 (2000预训练 + 2000微调)
FINETUNE_CHOICES_COUNT = 26 # 微调问答中的选项数量 (A-Z)

# --- 1. 加载和初步筛选数据 ---
print(f"Loading data from {SOURCE_FILE}...")
try:
    # 使用迭代器和tqdm显示加载进度
    # 数据量很大，我们只加载并处理需要的样本量，以节省内存
    data = []
    with open(SOURCE_FILE, 'r') as f:
        for line in tqdm(f, desc="Loading and filtering data"):
            record = json.loads(line)
            # 预处理步骤1: 筛选只有单个分类标签的论文
            if 'categories' in record and len(record['categories'].split()) == 1:
                data.append({
                    'id': record.get('id'),
                    'title': record.get('title'),
                    'authors': record.get('authors'),
                    'categories': record.get('categories'),
                    'abstract': record.get('abstract')
                })
            if len(data) >= TOTAL_SAMPLES_TO_PROCESS * 5: # 加载比所需更多的样本以确保随机性
                break
    
    if len(data) < TOTAL_SAMPLES_TO_PROCESS:
        print(f"Warning: Found only {len(data)} single-category papers, which is less than the required {TOTAL_SAMPLES_TO_PROCESS}.")
        # 如果样本不足，则使用所有找到的样本
        TOTAL_SAMPLES_TO_PROCESS = len(data)

    df = pd.DataFrame(data)
    print(f"Loaded {len(df)} single-category papers.")

except FileNotFoundError:
    print(f"Error: The source file '{SOURCE_FILE}' was not found.")
    print("Please download the dataset from 'https://www.kaggle.com/datasets/Cornell-University/arxiv' and place it in the same directory as this script.")
    exit()


# --- 2. 数据清洗和准备 ---
print("Cleaning and preparing data...")

# 预处理步骤2: 移除缺失关键信息的行
df.dropna(subset=['id', 'title', 'authors', 'categories', 'abstract'], inplace=True)

# 预处理步骤3: 清洗文本，去除多余的换行符和空格
def clean_text(text):
    return ' '.join(text.replace('\n', ' ').split())

for col in ['title', 'abstract', 'authors']:
    df[col] = df[col].apply(clean_text)

# 预处理步骤4: 随机抽样
if len(df) > TOTAL_SAMPLES_TO_PROCESS:
    df_sampled = df.sample(n=TOTAL_SAMPLES_TO_PROCESS, random_state=42)
else:
    df_sampled = df.copy()
    
print(f"Sampled {len(df_sampled)} papers for dataset generation.")

# 准备微调所需的唯一分类列表
all_categories = df['categories'].unique().tolist()
print(f"Found {len(all_categories)} unique categories for generating choices.")


# --- 3. 生成预训练数据集 ---
print(f"Generating {PRETRAIN_OUTPUT_FILE}...")
pretrain_data = df_sampled.head(TOTAL_SAMPLES_TO_PROCESS // 2)

with open(PRETRAIN_OUTPUT_FILE, 'w', encoding='utf-8') as f:
    for _, row in tqdm(pretrain_data.iterrows(), total=len(pretrain_data), desc="Writing pre-train data"):
        text_blob = (
            f"This is a paper with ID {row['id']}, titled \"{row['title']}\", submitted by {row['authors']}.\n"
            f"The paper belongs to the {row['categories']} category.\n\n"
            f"Abstract:\n{row['abstract']}"
        )
        json_record = {"text": text_blob}
        f.write(json.dumps(json_record, ensure_ascii=False) + '\n')

print(f"Successfully created {PRETRAIN_OUTPUT_FILE}")


# --- 4. 生成微调数据集 ---
print(f"Generating {FINETUNE_OUTPUT_FILE}...")
finetune_data = df_sampled.tail(TOTAL_SAMPLES_TO_PROCESS // 2)

def create_finetune_choices(correct_category, all_cats, num_choices):
    choices = {correct_category}
    while len(choices) < min(num_choices, len(all_cats)):
        choices.add(random.choice(all_cats))
    
    shuffled_choices = random.sample(list(choices), len(choices))
    
    options_dict = {}
    correct_answer_letter = ''
    for i, choice in enumerate(shuffled_choices):
        letter = string.ascii_uppercase[i]
        options_dict[letter] = choice
        if choice == correct_category:
            correct_answer_letter = letter
            
    return options_dict, correct_answer_letter

with open(FINETUNE_OUTPUT_FILE, 'w', encoding='utf-8') as f:
    for _, row in tqdm(finetune_data.iterrows(), total=len(finetune_data), desc="Writing fine-tune data"):
        choices, correct_letter = create_finetune_choices(row['categories'], all_categories, FINETUNE_CHOICES_COUNT)
        
        options_str = "\n".join([f"{letter}. {cat}" for letter, cat in choices.items()])
        
        human_prompt = (
            f"请根据以下论文信息，从选项中选择最合适的学科分类。\n\n"
            f"### 论文信息\n"
            f"- **标题**: {row['title']}\n"
            f"- **作者**: {row['authors']}\n"
            f"- **摘要**: {row['abstract']}\n\n"
            f"### 分类选项\n"
            f"{options_str}\n\n"
            f"你的回答 (仅一个字母):"
        )

        json_record = {
            "system": "你是一位专业的arXiv论文分类专家。你的任务是根据提供的论文标题、作者和摘要，从给定的选项中选择最准确的学科分类。请直接输出唯一正确的选项字母，不要包含任何其他解释或文本。",
            "conversation": [
                {
                    "human": human_prompt,
                    "assistant": correct_letter
                }
            ]
        }
        f.write(json.dumps(json_record, ensure_ascii=False) + '\n')

print(f"Successfully created {FINETUNE_OUTPUT_FILE}")
print("\nAll tasks completed!")
