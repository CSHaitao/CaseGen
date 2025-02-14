import re

def load_template(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

defense_template_path = 'eval/template/defense_judge_template.txt'
fact_template_path = 'eval/template/fact_judge_template.txt'
reasoning_template_path = 'eval/template/reasoning_judge_template.txt'
judgement_template_path = 'eval/template/judgement_judge_template.txt'

defense_template = load_template(defense_template_path)
fact_template = load_template(fact_template_path)
reasoning_template = load_template(reasoning_template_path)
judgement_template = load_template(judgement_template_path)

def use_defense_judge_template(prosecution, reference_defense, generated_defense):
    while '<' in generated_defense:
        generated_defense = re.sub(r"<antThinking>.*?</antThinking>", "", generated_defense,flags=re.S)
        generated_defense = re.sub(r"<.*?>", "", generated_defense,flags=re.S)
    prompt = defense_template.replace("{起诉书}", prosecution).replace("{参考答辩书}",reference_defense).replace("{AI助手撰写的答辩书}",generated_defense)
    #if 'antThinking' in prompt:
        #print("wrong" + generated_defense)
    return prompt

def use_fact_judge_template(reference_fact,generated_fact):
    while '<' in generated_fact:
        generated_fact = re.sub(r"<antThinking>.*?</antThinking>", "", generated_fact,flags=re.S)
        generated_fact = re.sub(r"<.*?>", "", generated_fact,flags=re.S)
    prompt = fact_template.replace("{参考答案}", reference_fact).replace("{审理事实}",generated_fact)
    return prompt

def use_reasoning_judge_template(reference_reasoning, generated_reasoning):
    while '<' in generated_reasoning:
        generated_reasoning = re.sub(r"<antThinking>.*?</antThinking>", "", generated_reasoning,flags=re.S)
        generated_reasoning = re.sub(r"<.*?>", "", generated_reasoning,flags=re.S)
    prompt = reasoning_template.replace("{参考答案}", reference_reasoning).replace("{判决说理部分}", generated_reasoning)
    return prompt

def use_judgement_judge_template(reference_judgement,generated_judgement):
    while '<' in generated_judgement:
        generated_judgement = re.sub(r"<antThinking>.*?</antThinking>", "", generated_judgement,flags=re.S)
        generated_judgement = re.sub(r"<.*?>", "", generated_judgement,flags=re.S)
    prompt = judgement_template.replace("{参考答案}", reference_judgement).replace("{AI助手撰写的判决结果部分}",generated_judgement)
    return prompt