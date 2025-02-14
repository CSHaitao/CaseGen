def load_template(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

defense_template_path = 'generate/template/defense_generate_template.txt'
fact_template_path = 'generate/template/fact_generate_template.txt'
reasoning_template_path = 'generate/template/reasoning_generate_template.txt'
judgement_template_path = 'generate/template/judgement_generate_template.txt'

defense_template = load_template(defense_template_path)
fact_template = load_template(fact_template_path)
reasoning_template = load_template(reasoning_template_path)
judgement_template = load_template(judgement_template_path)

def use_defense_template(prosecution, evidence):
    evidence_string = ""
    for i, (evidence_name, evidence_content) in enumerate(evidence.items(), 1):
        evidence_string += f"证据{i}：{evidence_name}\n{evidence_content}\n\n"
    prompt = defense_template.replace("{起诉状内容}", prosecution).replace("{证据内容}",evidence_string)
    return prompt

def use_fact_template(prosecution,defense,evidence):
    evidence_string = ""
    for i, (evidence_name, evidence_content) in enumerate(evidence.items(), 1):
        evidence_string += f"证据{i}：{evidence_name}\n{evidence_content}\n\n"
    prompt = fact_template.replace("{起诉状内容}", prosecution).replace("{答辩状内容}",defense).replace("{证据内容}",evidence_string)
    return prompt

def use_reasoning_template(prosecution, defense, fact):
    prompt = reasoning_template.replace("{起诉状内容}", prosecution).replace("{答辩状内容}", defense).replace("{审理事实}", fact)
    return prompt

def use_judgement_template(fact,reasoning):
    prompt = judgement_template.replace("{审理事实}", fact).replace("{裁判分析}",reasoning)
    return prompt

