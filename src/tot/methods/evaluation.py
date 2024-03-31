import re
import json
import string
from collections import Counter
from sklearn.metrics import f1_score
from tot.models import gpt

def normalize_answer(s):

    def remove_articles(text):
        return re.sub(r'\b(a|an|the)\b', ' ', text)

    def white_space_fix(text):
        return ' '.join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def f1_score_c(prediction, ground_truth):
    normalized_prediction = normalize_answer(prediction)
    normalized_ground_truth = normalize_answer(ground_truth)

    ZERO_METRIC = (0, 0, 0)

    if normalized_prediction in ['true', 'false', 'unknown'] and normalized_prediction != normalized_ground_truth:
        return ZERO_METRIC
    if normalized_ground_truth in ['true', 'false', 'unknown'] and normalized_prediction != normalized_ground_truth:
        return ZERO_METRIC

    prediction_tokens = normalized_prediction.split()
    ground_truth_tokens = normalized_ground_truth.split()
    common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return ZERO_METRIC
    precision = 1.0 * num_same / len(prediction_tokens)
    recall = 1.0 * num_same / len(ground_truth_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1, precision, recall

def update_answer(metrics, prediction, gold):
    # em = exact_match_score(prediction, gold)
    f1, prec, recall = f1_score_c(prediction, gold)
    # metrics['em'] += float(em)
    metrics['f1'] += f1
    metrics['prec'] += prec
    metrics['recall'] += recall
    metrics['N'] += 1
    return f1, prec, recall

def update_score(metrics, score):
    metrics['score'] += score
    return score


def compute_f1_strategy(data):
    metrics = {'f1': 0, 'prec': 0, 'recall': 0, 'N': 0}
    total_score = 0
    num_scores = 0
    running_num_score = 0
    running_total_score = 0

    for entry in data:
        for item in entry:
            if 'answer' in item:
                answer = item['answer'][0]
                if 'true' in answer.lower():
                    actual_answer = 'true'
                elif 'false' in answer.lower():
                    actual_answer = 'false'
                else:
                    actual_answer = 'unknown'

                expected_answer = str(item['answer_gt'])
                # print(actual_answer)
                # print(expected_answer)
                update_answer(metrics, actual_answer, expected_answer)
            
            if "score" in item:
                score = item["score"]
                if score != 0:
                    total_score += score
                    num_scores += 1
                else:
                    total_score += running_total_score / max(running_num_score, 1)
                    num_scores += 1
                
                running_total_score = total_score
                running_num_score = num_scores

    results = []
    for k in metrics.keys():
        metrics[k] /= metrics['N']
    results.append(metrics)

    average_score = total_score / num_scores

    return results, average_score

def compute_f1_gsm8k(data):
    metrics = {'f1': 0, 'prec': 0, 'recall': 0, 'N': 0}
    total_score = 0
    num_scores = 0
    running_num_score = 0
    running_total_score = 0

    for entry in data:
        for item in entry:
            if 'answer' in item:
                answer = item['answer'][0]
                matches = re.findall(r'\b\d+\b', answer)
                if matches:
                    actual_answer = matches[-1]
                else:
                    actual_answer = 'unknown'     
                expected_answer = str(item['answer_gt'])
                # print('actual answer', actual_answer)
                # print('expected answer', expected_answer)
                update_answer(metrics, actual_answer, expected_answer)
            
            if "score" in item:
                score = item["score"]
                if score != 0:
                    total_score += score
                    num_scores += 1
                else:
                    total_score += running_total_score / max(running_num_score, 1)
                    num_scores += 1
                
                running_total_score = total_score
                running_num_score = num_scores

    results = []
    for k in metrics.keys():
        metrics[k] /= metrics['N']
    results.append(metrics)

    average_score = total_score / num_scores

    return results, average_score

def compute_f1_researchy(data):
    total_score = 0
    num_scores = 0
    running_num_score = 0
    running_total_score = 0

    for entry in data:
        for item in entry:
            if "score" in item:
                score = item["score"]
                if score != 0:
                    total_score += score
                    num_scores += 1
                else:
                    total_score += running_total_score / max(running_num_score, 1)
                    num_scores += 1
                
                running_total_score = total_score
                running_num_score = num_scores

    average_score = total_score / num_scores

    return average_score


def compute_comparison(score, dfs_ans, cot_ans, io_ans, question, ans_gt, round):
    score = {'dfs': 0, 'cot': 0, 'io': 0}
    print('comparing')
    pattern_1 = r'<Score1>(0|1)</Score1>'
    pattern_2 = r'<Score2>(0|1)</Score2>'
    compiled_pattern_1 = re.compile(pattern_1, re.IGNORECASE)
    compiled_pattern_2 = re.compile(pattern_2, re.IGNORECASE)
    # print(question, ans_gt)

    comparison_lists = [
        [[dfs_ans, cot_ans], [cot_ans, io_ans], [dfs_ans, io_ans]],
        [[cot_ans, io_ans], [io_ans, dfs_ans], [cot_ans, dfs_ans]],
        [[io_ans, dfs_ans], [dfs_ans, cot_ans], [io_ans, cot_ans]]
    ]

    compare = comparison_lists[round]

    for idx, pair in enumerate(compare):
        print(pair[0], pair[1])
        prompt = eval_comparison_prompt.format(Question=question, ReferenceAnswer=ans_gt, CandidateAnswer1=pair[0], CandidateAnswer2=pair[1])
        # print(prompt)
        res = gpt(prompt, temperature=0)
        print(res)
        match_1 = re.search(compiled_pattern_1, res[0])
        score_1 = float(match_1.group(1)) if match_1 else 0

        match_2 = re.search(compiled_pattern_2, res[0])
        score_2 = float(match_2.group(1)) if match_2 else 0

        # Update scores based on the comparison list being used
        if round == 0:  # First comparison list
            if idx == 0:
                score['dfs'] += score_1
                score['cot'] += score_2
            elif idx == 1:
                score['cot'] += score_1
                score['io'] += score_2
            elif idx == 2:
                score['dfs'] += score_1
                score['io'] += score_2
        elif round == 1:  # Second comparison list
            if idx == 0:
                score['cot'] += score_1
                score['io'] += score_2
            elif idx == 1:
                score['io'] += score_1
                score['dfs'] += score_2
            elif idx == 2:
                score['cot'] += score_1
                score['dfs'] += score_2
        elif round == 2:  # Third comparison list
            if idx == 0:
                score['io'] += score_1
                score['dfs'] += score_2
            elif idx == 1:
                score['dfs'] += score_1
                score['cot'] += score_2
            elif idx == 2:
                score['io'] += score_1
                score['cot'] += score_2

    print(f'score: {score}')
    return score



eval_score_prompt = '''
Question: {Question}
#####################
Reference Answer (assumed to be true): {ReferenceAnswer}
Candidate Answer: {CandidateAnswer}
#####################
Guidelines:
You are evaluating the explaianability of the Candidate Answer. 
A truly explainable answer must clearly show the reasoning steps that led to the answer. You always prefer Candidate Answers that explain their reasoning process.
If no explanation of the reasoning strategy is there assign a very low score.
If the reasoning process is shown and is structured, clear and understandable assign a high score.
If the reasoning process is shown, is clear and contains extremely relevant, fully exhaustive and no redundant information assign a very high score.
##################### Instructions: Above is a Candidate Answer to the Question: {Question}.
Please read it carefully along with the Guidelines for how to evaluate an answer’s quality. Then:
1. Critique the Candidate Answer in detail with respect to the Guidelines between "<Critique>" and "</Critique>" tags. Comment on whether the reasoning process is shown and whether it is clear, relevant, exhaustive and non-redundant.
2. Summarise how well the Candidate Answer adheres to the Guidelines in general, between "<Explanation>" and "</Explanation>" tags."
3. Finally, score the Candidate Answer on 1-100, where 100 is a perfect Answer that aligns with the Guidelines and 0 is an Answer with no reasoning steps. Indicate the score between "<Score>" and "</Score>" tags.
When you are finished, conclude your response with "=====".
<Critique1>'''


eval_comparison_prompt = '''
Question: {Question}
#####################
Reference Answer (assumed to be true): {ReferenceAnswer}
Candidate Answer 1: {CandidateAnswer1}
Candidate Answer 2: {CandidateAnswer2}
#####################
Guidelines:
You are evaluating the explaianability of the Candidate Answer. 
A truly explainable answer must show the reasoning steps that led to the answer. You always prefer Candidate Answers that explain their reasoning process.
If no explanation of the reasoning strategy is there assign a very low score.
If the reasoning process is shown and is structured, clear and understandable assign a high score.
If the reasoning process is shown, is clear and contains extremely relevant, fully exhaustive and no redundant information assign a very high score.
##################### Instructions: Above are 2 Candidate Answers to the Question: {Question}.
Please read them carefully along with the Guidelines for how to evaluate an answer’s quality. Then:
1. Critique each Candidate Answer in detail with respect to the Guidelines between "<CritiqueX>" and "</CritiqueX>" tags where X is the Candidate Answer number. Comment on whether the reasoning process is shown and whether it is clear, relevant, exhaustive and non-redundant.
2. Explain which Candidate Answer is better and why, i.e. how well it adheres to the Guidelines, between "<Explanation>" and "</Explanation>" tags. 
3. Finally, assign the best Candidate Answer the score of 1 and the worst Candidate Answer the score of 0. If one of the Candidate Answers does not show its reasoning process, assign it the score 0. Indicate the score between "<ScoreX>" and "</ScoreX>" tags where X is the Candidate Answer number. There should always be a Candidate Answer with the score 1 and one with the score 0, they cannot both be scored 1 or both be scored 0. 
Make sure to address all 2 Candidate Answers. When you are finished, conclude your response with "=====".
<Critique1>'''