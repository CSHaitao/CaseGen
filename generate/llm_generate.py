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


class GLM4_API:
    def __init__(self, api_key):
        self.client = ZhipuAI(api_key=api_key)
    
    def chat(self, query, model):
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": query},
            ],
            stream=False,
            temperature=0,
            top_p=0,
            do_sample=False,
            tools=[]
        )
        try:
            return response.choices[0].message.content
        except:
            raise Exception(json.loads(response.text)["message"])

class OpenAI_API:
    def __init__(self, api_key):
        self.base_url = "https://svip.xty.app/v1"
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=api_key,
            http_client=httpx.Client(
                base_url=self.base_url,
                follow_redirects=True,
            ),
        )
    
    def chat(self, query, model):
        response = self.client.chat.completions.create(
            model=model,
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

class SiliconFlow_API:
    def __init__(self, api_key):
        self.url = "https://api.siliconflow.cn/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def chat(self, query, model):
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ],
            "model": model,
            "temperature": 0,
            "top_k": -1,
            "top_p": 1
        }
        response = requests.post(self.url, json=payload, headers=self.headers)
        try:
            return json.loads(response.text)["choices"][0]["message"]["content"]
        except:
            raise Exception(json.loads(response.text)["message"])

class XIAOHONGSHU_API:
    def __init__(self, api_key):
        self.base_url = "http://redservingapi.devops.xiaohongshu.com/v1"
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=api_key
        )
    
    def chat(self, query, model):
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ],
            stream=False,
            temperature=0,
            max_tokens=5000,
            top_p=0.0001,
            tools=[]
        )
        try:
            return response.choices[0].message.content
        except:
            raise Exception(response)

class ChatClient:
    def __init__(self, service, api_key):
        self.api_key = api_key
        self.service = service.lower()
        if self.service == "glm4":
            self.client = GLM4_API(api_key)
        elif self.service == "openai":
            self.client = OpenAI_API(api_key)
        elif self.service == "siliconflow":
            self.client = SiliconFlow_API(api_key)
        elif self.service == "xiaohongshu":
            self.client = XIAOHONGSHU_API(api_key)
        else:
            raise ValueError("Unsupported service")

    def chat(self, query, model=None):
        return self.client.chat(query, model)


def create_chat_client(model_name,api_key):
    if model_name in ["glm-4-flash","glm-4"]:
        print("use glm")
        return ChatClient("glm4", api_key)
    elif model_name in ["gpt-4o-mini","gpt-3.5-turbo","claude-3-5-sonnet-20240620"]:
        print("use openai")
        return ChatClient("openai", api_key)
    elif model_name in ["Qwen/Qwen2.5-7B-Instruct","meta-llama/Meta-Llama-3.1-8B-Instruct","Qwen/Qwen2.5-14B-Instruct"]:
        print("use silicon")
        return ChatClient("siliconflow", api_key)
    elif model_name in ["qwen2.5-72b-instruct","llama-3.3-70b-instruct"]:
        return ChatClient("xiaohongshu",api_key)
    else:
        raise ValueError(f"Unsupported model name: {model_name}")

def ask_prompt(json_object, chat_client, model_name):
    prompt = json_object['prompt']
    while True:
        try:
            r = chat_client.chat(prompt, model_name)
            break
        except Exception as e:
            if 'API请求过多' in str(e) or 'Connection' in str(e):
                print("Connection error" + str(e))
                time.sleep(5)
                continue 
            elif 'PM'in str(e): 
                time.sleep(50) 
                continue
            elif 'length' in str(e):
                print(str(e)+ "截断,原长度" + str (len(prompt)))
                leng = int(len(prompt) * 0.9)
                prompt = prompt[:int (leng / 2)] + prompt[ 0-(int(leng / 2)):] 
                continue
            elif '敏感' in str(e):
                print('敏感提问')
                r = "Error occurred"
                break
            else:
                print(f"Error processing ID {json_object['id']}: {str(e)}")
                r = "Error occurred"
                break
    return {'id': json_object['id'], 'response': r}

def ask_file(input_file_path, output_file_path,model_name,api_key):
    processed_ids = set()

    if os.path.exists(output_file_path):
        with open(output_file_path, 'r', encoding='utf-8') as out_file:
            for line in out_file:
                result = json.loads(line)
                processed_ids.add(result['id'])


    with open(input_file_path, 'r', encoding='utf-8') as file:
        json_data = [json.loads(line) for line in file.readlines()]
    
    results = []
    chat_client = create_chat_client(model_name,api_key)
    with tqdm(total=len(json_data) - len(processed_ids), desc="Processing") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
            futures = [executor.submit(ask_prompt, json_object, chat_client, model_name) for json_object in json_data if json_object['id'] not in processed_ids]
                
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
                pbar.update(1)
                
                # Write each result to the output file immediately
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
    parser = argparse.ArgumentParser(description='处理模型名称和任务名称')
    parser.add_argument('model_name', type=str, help='要使用的模型名称')
    parser.add_argument('api_key', type=str, help='请输入API密钥')
    parser.add_argument('task_name', type=str, nargs='?', help='要处理的任务名称 (defense, fact, reasoning, judgement)，如果不指定则处理所有任务')
    args = parser.parse_args()
    model_name = args.model_name
    task_name = args.task_name
    api_key = args.api_key

    # 定义输入和输出文件路径
    output_dir = f"generate/generated_data/{model_name}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    tasks = ['defense', 'fact', 'reasoning', 'judgement']
    if task_name in tasks:
        tasks = [task_name]  # 只处理指定的任务

    for task in tasks:
        output_file_path = os.path.join(output_dir, f"{task}.json")
        ask_file(f"generate/prompt/{task}_generate_prompt.json", output_file_path, model_name,api_key)


if __name__ == "__main__":
    main()

# python generate/llm_generate.py glm-4-flash API_KEY reasoning
