from use_template import (
    use_defense_judge_template,
    use_fact_judge_template,
    use_reasoning_judge_template,
    use_judgement_judge_template
)
import json
import os
import argparse
data_len = 500
original_data_path = "data/"

def make_prompt(original_data_path, generated_file_path, output_file_path, content_type):
    original_file = open(original_data_path,'r', encoding='utf-8').readlines()
    generated_file = open(generated_file_path,'r', encoding='utf-8').readlines()

    if os.path.exists(output_file_path):
        os.remove(output_file_path)
        
    with open(output_file_path,'a', encoding='utf-8') as out_file:
        for id in range(0,data_len):
            original_dict = json.loads(original_file[id])
            generated_dict = json.loads(generated_file[id])
            if content_type == 'defense':
                prompt = use_defense_judge_template(original_dict['prosecution'],original_dict['defense'],generated_dict['response'])
            elif content_type == 'fact':
                prompt = use_fact_judge_template(original_dict['fact'],generated_dict['response'])
            elif content_type == 'reasoning':
                prompt = use_reasoning_judge_template(original_dict['reasoning'],generated_dict['response'])
            elif content_type == 'judgement':
                prompt = use_judgement_judge_template(original_dict['judgement'],generated_dict['response'])
            else:
                raise ValueError("未知的内容类型: {}".format(content_type))
            out_file.write(json.dumps({"id": id,"type": content_type, "prompt": prompt}, ensure_ascii=False) + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成提示信息")
    parser.add_argument("model_name", type=str, help="评测对象模型")
    parser.add_argument('task_name', type=str, nargs='?', help='要处理的任务名称 (defense, fact, reasoning, judgement)，如果不指定则处理所有任务')
    args = parser.parse_args()
    model_name = args.model_name
    task_name = args.task_name

    tasks = ['defense', 'fact', 'reasoning', 'judgement']
    if task_name in tasks:
        tasks = [task_name] 

    generated_dir = f"generate\\generated_data\\{model_name}"
    output_dir = f"eval\\prompt\\{model_name}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for task in tasks:
        generated_file_path = os.path.join(generated_dir, f"{task}.json")
        output_file_path = os.path.join(output_dir, f"{task}_eval_prompt.json")
        make_prompt(original_data_path, generated_file_path, output_file_path, task)


# python eval/make_prompt.py glm-4-flash defense
