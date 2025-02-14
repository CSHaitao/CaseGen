# 导入所需的函数
from use_template import (
    use_defense_template,
    use_fact_template,
    use_reasoning_template,
    use_judgement_template
)
import json
import os
import argparse

input_file_path = "data/data_0130_500.json"

def make_prompt(input_file_path, output_file_path, content_type):
    file = open(input_file_path,'r', encoding='utf-8')
    if os.path.exists(output_file_path):
        os.remove(output_file_path)
    with open(output_file_path,'a', encoding='utf-8') as out_file:
        for line in file.readlines():
            a_dict = json.loads(line)
            # dict_keys(['id', 'title', 'full_text', 'prosecution', 'defense', 'fact', 'reasoning', 'judgement', 'event', 'evidence'])
            id = a_dict['id']
            if content_type == 'defense':
                prompt = use_defense_template(a_dict['prosecution'],a_dict['evidence'])
            elif content_type == 'fact':
                prompt = use_fact_template(a_dict['prosecution'],a_dict['defense'],a_dict['evidence'])
            elif content_type == 'reasoning':
                prompt = use_reasoning_template(a_dict['prosecution'],a_dict['defense'],a_dict['fact'])
            elif content_type == 'judgement':
                prompt = use_judgement_template(a_dict['fact'],a_dict['reasoning'])
            else:
                raise ValueError("未知的内容类型: {}".format(content_type))
            out_file.write(json.dumps({"id": id,"type": content_type, "prompt": prompt}, ensure_ascii=False) + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='任务名称')
    parser.add_argument('task_name', type=str, nargs='?', help='要处理的任务名称 (defense, fact, reasoning, judgement)，如果不指定则处理所有任务')
    args = parser.parse_args()
    task_name = args.task_name

    tasks = ['defense', 'fact', 'reasoning', 'judgement']
    if task_name in tasks:
        tasks = [task_name] 

    for task in tasks:
        output_file_path = f"generate/prompt/{task_name}_generate_prompt.json"
        make_prompt(input_file_path, output_file_path, task)


    # python generate/make_prompt.py reasoning
