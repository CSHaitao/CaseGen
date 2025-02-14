import json
import os
from zhipuai import ZhipuAI
import httpx
from tqdm import tqdm  # 用于进度条
import concurrent.futures  # 并行处理
import requests
from openai import OpenAI
import argparse
import time


class OpenAI_API:
    def __init__(self, api_key):
        self.base_url = "https://one-api.glm.ai:/v1"
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=api_key,
        )
    
    def chat(self, query):
        response = self.client.chat.completions.create(
            model="gpt-4o-2024-11-20",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ],
            stream=False,
            temperature=0,
            top_p=0,
            tools=[]
        )
        try:
            return response.choices[0].message.content
        except:
            raise Exception(json.loads(response.text)["message"])

class ChatClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = OpenAI_API(api_key)

    def chat(self, query):
        return self.client.chat(query)

def ask_prompt(json_object, chat_client):
    prompt = json_object['prompt']
    max_retries = 10  # 最大重试次数
    attempts = 0  # 当前尝试次数
    print(prompt)
    while attempts < max_retries:
        try:
            r = chat_client.chat(prompt)
    
        except Exception as e:
            attempts += 1  # 记录尝试次数
            r = str(e)
            continue
    else:
        print(f"ID {json_object['id']} 超过最大尝试次数 ({max_retries})，终止重试")
        r = "Error occurred"

    return {'id': json_object['id'], 'response': r}

def ask_file(input_file_path, output_file_path,api_key):
    chat_client = ChatClient(api_key)
    processed_ids = set()

    if os.path.exists(output_file_path):
        with open(output_file_path, 'r', encoding='utf-8') as out_file:
            for line in out_file:
                result = json.loads(line)
                processed_ids.add(result['id'])

    with open(input_file_path, 'r', encoding='utf-8') as file:
        json_data = [json.loads(line) for line in file.readlines()]
    
    results = []
    
    with tqdm(total=len(json_data) - len(processed_ids), desc="Processing") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(ask_prompt, json_object, chat_client) for json_object in json_data if json_object['id'] not in processed_ids]
                
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
                pbar.update(1)
                
                with open(output_file_path, 'a', encoding='utf-8') as out_file:
                    out_file.write(json.dumps(result, ensure_ascii=False) + '\n')
    
    print(f"总共处理了 {len(results)} 个结构体。")
    with open(output_file_path, 'r', encoding='utf-8') as out_file:
        sorted_results = sorted((json.loads(line) for line in out_file), key=lambda x: x['id'])
    
    with open(output_file_path, 'w', encoding='utf-8') as out_file:
        for result in sorted_results:
            out_file.write(json.dumps(result, ensure_ascii=False) + '\n')
    print(f"所有结构体按ID排序写入完成。")


def main():
    parser = argparse.ArgumentParser(description='Process model name')
    parser.add_argument('model_name', type=str, help='Name of the model to use')
    parser.add_argument('api_key', type=str, help='请输入API密钥')
    parser.add_argument('task_name', type=str, nargs='?', help='要处理的任务名称 (defense, fact, reasoning, judgement)，如果不指定则处理所有任务')
    args = parser.parse_args()
    model_name = args.model_name
    task_name = args.task_name
    api_key = args.api_key

    # Define input and output file paths
    input_dir = f"eval/prompt/{model_name}"
    output_dir = f"eval/llm_eval_result/{model_name}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    tasks = ['defense', 'fact', 'reasoning', 'judgement']
    if task_name in tasks:
        tasks = [task_name] 

    for task in tasks:
        input_file_path = os.path.join(input_dir, f"{task}_eval_prompt.json")
        output_file_path = os.path.join(output_dir, f"{task}.json")
        ask_file(input_file_path, output_file_path,api_key)


    

if __name__ == "__main__":
    main()
    
# python eval/llm_eval.py glm-4-flash API_KEY defense
