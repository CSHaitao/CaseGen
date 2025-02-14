from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import jieba
import json
import os
from rouge_score import rouge_scorer
from bert_score import score as bert_score
import argparse
from tqdm import tqdm  # 导入 tqdm

data_len = 500
# 定义不同的权重组合
weights_list = [
    (1, 0, 0, 0),  # 1-gram
    (0, 1, 0, 0),  # 2-gram
    (0, 0, 1, 0),  # 3-gram
    (0, 0, 0, 1)   # 4-gram
]
original_data_path = "data/data_0130_500.json"

def process_one_structure(id, reference, generated):
    if generated  == "Error occurred":
        return {'id': id, 'bleu': -1, "rouge": -1, "bertscore": -1} 
    reference_tokens = list(jieba.cut(reference))
    generated_tokens = list(jieba.cut(generated))
    smoothie = SmoothingFunction().method4
    
    bleu_scores = {}

    for i, weights in enumerate(weights_list):
        score_smooth = sentence_bleu([reference_tokens], generated_tokens, weights=weights, smoothing_function=smoothie)
        bleu_scores[f'{i + 1}_gram'] = score_smooth

    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=False) 
    rouge_scores = scorer.score(reference, generated) # Score(precision=0.0, recall=0.0, fmeasure=0.0)

    # 计算BERTScore
    P, R, F1 = bert_score([generated], [reference], lang="zh", verbose=False,model_type="bert-base-chinese")
    bert_scores = {'precision': P.mean().item(), 'recall': R.mean().item(), 'f1': F1.mean().item()}
    
    # 将分数字典写入文件
    return {'id': id, 'bleu': bleu_scores, "rouge": rouge_scores, "bertscore": bert_scores} 

def process_file(original_data_path,generated_file_path, output_file_path,content_type):
    
    original_file = open(original_data_path,'r', encoding='utf-8').readlines()
    generated_file = open(generated_file_path,'r', encoding='utf-8').readlines()

    processed_ids = set()
    if os.path.exists(output_file_path):      
        with open(output_file_path, 'r', encoding='utf-8') as out_file:
            for line in out_file:
                result = json.loads(line)
                processed_ids.add(result['id'])


    with open(output_file_path,'a', encoding='utf-8') as out_file:
        for id in tqdm(range(0,data_len)):
            if id in processed_ids:
                continue
            original_dict = json.loads(original_file[id])
            generated_dict = json.loads(generated_file[id])
            reference_string = original_dict[content_type]
            generated_string = generated_dict['response']
            eval_result = process_one_structure(id, reference_string, generated_string)
            out_file.write(json.dumps(eval_result, ensure_ascii=False))
            out_file.write('\n')

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

    
    generated_dir = f"generate/generated_data/{model_name}"
    output_dir = f"eval/eval_result/{model_name}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for task in tasks:
        generated_file_path = os.path.join(generated_dir, f"{task}.json")
        output_file_path = os.path.join(output_dir, f"{task}_eval_result.json")
        process_file(original_data_path, generated_file_path, output_file_path, task)

# python eval/bleu_rouge_bert_eval.py glm-4-flash defense