import json
import argparse
import pandas as pd
import re
import os

output_file_path_xlsx = f"excel/llm_as_judge.xlsx"

def read_structures(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        buffer = ""
        for line in file:
            buffer += line
            if buffer.strip().endswith('}'):
                try:
                    json_object = json.loads(buffer)
                    yield json_object, buffer
                    buffer = ""
                except json.JSONDecodeError:
                    continue

def add_key(input_path,output_path, task_type):
    if os.path.exists(output_path):
        os.remove(output_path)

    with open(output_path, 'a', encoding='utf-8') as out_file:
        for _, (json_object, _) in enumerate(read_structures(input_path), 1):
            answer = json_object['response']
            if '<think>' in answer:
                answer = re.sub(r"<think>.*?</think>", "", answer,flags=re.S)
            
            left_bracket_index = answer.rfind('{')
            if left_bracket_index != -1:
                right_bracket_index = answer[left_bracket_index:].find('}')
                try:
                    match = answer[left_bracket_index: left_bracket_index + right_bracket_index + 1].replace('\'','\"').replace('\\','')
                    match = re.sub(r'(?<=\D)([0-9]|10)分', r'\1', match)
                    if match.startswith('{{'):
                        match = match[1:]  # 去除一个
                    json_result = json.loads(match)
                    if '综合得分' not in json_result:
                        json_result['综合得分'] = -1
                    if task_type =='defense':
                        if '事实准确性' not in json_result:
                            if '事实正确性' in json_result:
                                json_result['事实准确性'] = json_result['事实正确性']
                            else:
                                json_result['事实准确性'] = -1
                                print(json_result)
                        if '法律关系准确性'not in json_result:
                            if '法律关系正确性' in json_result:
                                json_result['法律关系准确性'] = json_result['法律关系正确性']
                            else :
                                json_result['法律关系准确性'] = -1
                                print(json_result)
                        if '逻辑性' not in json_result:
                            json_result['逻辑性'] = -1
                            print(json_result)
                        if '完备性' not in json_result:
                            json_result['完备性'] = -1
                            print(json_result)
                    elif task_type == 'fact':
                        if '事实准确性' not in json_result:
                            if '事实正确性' in json_result:
                                json_result['事实准确性'] = json_result['事实正确性']
                            else:
                                json_result['事实准确性'] = -1
                                print(json_result)
                        if '相关性' not in json_result:
                            json_result['相关性'] = -1
                            print(json_result)
                        if '逻辑性' not in json_result:
                            json_result['逻辑性'] = -1
                            print(json_result)
                    elif task_type == 'reasoning':
                        if '争议焦点准确性' not in json_result:
                            if '争议焦点正确性' in json_result:
                                json_result['争议焦点准确性'] = json_result['争议焦点正确性']
                            else:
                                json_result['争议焦点准确性'] = -1
                                print(json_result)
                        if '法律关系准确性' not in json_result:
                            if '法律关系正确性' in json_result:
                                json_result['法律关系准确性'] = json_result['法律关系正确性']
                            else:
                                json_result['法律关系准确性'] = -1
                                print(json_result)
                        if '逻辑性' not in json_result:
                            json_result['逻辑性'] = -1
                            print(json_result)
                        if '伦理性' not in json_result:
                            json_result['论理性'] = -1
                            print(json_result)
                    elif task_type == 'judgement':
                        if '判决结果准确性' not in json_result:
                            if '判决问题准确性' in json_result:
                                json_result['判决结果准确性'] = json_result['判决问题准确性']
                            elif '判决结果正确性' in json_result:
                                json_result['判决结果准确性'] = json_result['判决结果正确性']
                            else:
                                json_result['判决结果准确性'] = -1
                                print(json_result)
                        if '引用法条完整性和准确性' not in json_result:
                            if '引用法条完整性和正确性' in json_result:
                                json_result['引用法条完整性和准确性'] = json_result['引用法条完整性和正确性']
                            elif'引用法条完整正确确性' in json_result:
                                json_result['引用法条完整性和准确性'] = json_result['引用法条完整正确性']
                            elif '引用法条完整性' in json_result:
                                json_result['引用法条完整性和准确性'] = json_result['引用法条完整性']
                            elif '引用法条完整准确性' in json_result:
                                json_result['引用法条完整性和准确性'] = json_result['引用法条完整准确性']
                            else:
                                json_result['引用法条完整性和准确性'] = -1
                                print(json_result)
                    json_object.update(json_result)
                except Exception:
                    json_object['引用法条完整性和准确性'] = -1
                    json_object['判决结果准确性'] = -1
                    json_object['争议焦点准确性'] = -1
                    json_object['相关性'] = -1
                    json_object['事实准确性'] = -1
                    json_object['法律关系准确性'] = -1
                    json_object['逻辑性'] = -1
                    json_object['伦理性'] = -1
                    json_object['完备性'] = -1
                    json_object['可负责性'] = -1
                    json_object['综合得分'] = -1
            else:
                json_object['引用法条完整性和准确性'] = -1
                json_object['判决结果准确性'] = -1
                json_object['相关性'] = -1
                json_object['争议焦点准确性'] = -1
                json_object['事实准确性'] = -1
                json_object['法律关系准确性'] = -1
                json_object['逻辑性'] = -1
                json_object['伦理性'] = -1
                json_object['完备性'] = -1
                json_object['可负责性'] = -1
                json_object['综合得分'] = -1

            out_file.write(json.dumps(json_object, ensure_ascii=False))
            out_file.write('\n')

def count_scores(input_path):
    score_count = {}
    for _, (json_object, _) in enumerate(read_structures(input_path), 1):
        score = json_object.get('综合得分', None)
        if score == -1:
            continue
        if score is not None:
            if score in score_count:
                score_count[score] += 1
            else:
                score_count[score] = 1
    return score_count

def main():
    parser = argparse.ArgumentParser(description='Process model name')
    parser.add_argument('model_name', type=str, help='Name of the model to use')
    parser.add_argument('task_name', type=str, nargs='?', help='要处理的任务名称 (defense, fact, reasoning, judgement)，如果不指定则处理所有任务')
    args = parser.parse_args()
    model_name = args.model_name
    task_name = args.task_name

    output_dir = f"eval/llm_eval_result/{model_name}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    tasks = ["defense", "fact","reasoning",  "judgement"]#"reasoning", 
    if task_name in tasks:
        tasks = [task_name] 

    for task in tasks:
        input_file_path = os.path.join(output_dir, f"{task}.json")
        output_file_path = os.path.join(output_dir, f"{task}_handled.json")
        
        add_key(input_file_path, output_file_path,task)
        with open(output_file_path, 'r', encoding='utf-8') as file:
            json_data = [json.loads(line) for line in file.readlines()]
            
        if task == 'defense':
            keys = ['事实准确性', '法律关系准确性', '逻辑性', '完备性', '综合得分']
        elif task =='fact':
            keys = ['事实准确性', '相关性', '逻辑性', '综合得分']
        elif task == 'reasoning':
            keys = ['争议焦点准确性', '法律关系准确性', '逻辑性', '伦理性', '综合得分']
        elif task == 'judgement':
            keys = ['判决结果准确性', '引用法条完整性和准确性', '综合得分']
        
        total_scores = {}
        for key in keys:
            total_scores[key] = {'总分': 0, 'count': 0}
            
        for score_object in json_data:
            try:
                for key in keys:
                    if score_object[key] != -1:
                        total_scores[key]['总分'] += score_object[key]
                        total_scores[key]['count'] += 1
            except Exception as e:
                raise Exception(f"score_object：{score_object} {str(e)}")

        new_data = {
            "模型名": model_name, 
            **{key: total_scores[key]['总分'] / total_scores[key]['count'] if total_scores[key]['count'] > 0 else 0 for key in keys}
        }

        try:
            df = pd.read_excel(output_file_path_xlsx, sheet_name=f"{task}")
        except:
            df = pd.DataFrame()
        
        new_row = pd.DataFrame(new_data, index=[0])
        df = pd.concat([df, new_row], ignore_index=True)
        
        if not os.path.exists(output_file_path_xlsx):
            parent_dir = os.path.dirname(output_file_path_xlsx)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
            with pd.ExcelWriter(output_file_path_xlsx, mode='w', engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=task, index=False)
        else:
            with pd.ExcelWriter(output_file_path_xlsx, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name=task, index=False)
        
        print(f"结果已保存到 {output_file_path_xlsx}")
        
        score_distribution = count_scores(output_file_path)
        sorted_distribution = dict(sorted(score_distribution.items()))
        print(f"每个分数的数量分布 ({task}):")
        total_score = 0
        total_count = 0
        for score, count in sorted_distribution.items():
            print(f"分数: {score}, 数量: {count}")
            total_score += score * count 
            total_count += count 
        average_score = total_score / total_count if total_count > 0 else 0 
        print(f"平均分 ({task}): {average_score:.2f}")
    

if __name__ == "__main__":
    main()

# python eval/llm_eval_handle.py glm-4