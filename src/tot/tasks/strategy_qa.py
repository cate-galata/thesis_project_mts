import re
import os
import json
from tot.tasks.base import Task, DATA_PATH
from tot.prompts.strategy_qa import * 
from tot.models import gpt
from tot.methods.evaluation import eval_score_prompt

def get_current_question(y: str) -> str:
    last_line = y.strip().split('\n')[-1]
    return last_line.split('left: ')[-1].split(')')[0]

class StrategyQAEnv:
    def __init__(self, file='strategyqa_train.json'):
        path = os.path.join(DATA_PATH, 'strategy_qa', file)
        self.file = json.load(open(path))
        self.n = len(self.file)
        self.cache = {}
        self.idx = None
        self.times = 0
        self.prompt_status_cache = {}

    def __len__(self):
        return self.n
    
    def reset(self, idx, decomp=None, status=None, steps=None):
        self.idx = idx
        self.cache = {}
        self.data = self.file[idx]['question']
        # ground truth values
        self.ans_gt = self.file[idx]['answer']
        self.decomp_gt = self.file[idx]['decomposition']
        self.facts_gt = self.file[idx]['facts']
        
        self.decomp = self.data
        self.ans = ""
        self.steps = 0
        self.status = [0] * 10  # 0: unfilled; 1: filled; 2: filled then changed
        if decomp is not None:
            self.decomp = decomp
            # self.ans = self.get_ans(self.decomp)
        if status is not None:
            self.status = status
        if steps is not None:
            self.steps = steps
        return self.render()
    

    def prompt_status(self):
        count = {'sure': 0, 'maybe': 0, 'impossible': 0}
        prompt = value_prompt.format(input=self.decomp)
        print(prompt)
        if prompt in self.prompt_status_cache:
            res = self.prompt_status_cache[prompt]
        else:
            res = (gpt(prompt)[0]).lower()
            print(res)
            self.prompt_status_cache[prompt] = res

        res_n = res.split('\n')[-1].strip() # extract sure, maybe, impossible from the value prompt output
        pattern = r'\b(sure|maybe|impossible)\b'
        match = re.search(pattern, res_n)
        if match:
            res_n = match.group(1)
        else:
            print("No match found.")
        if res_n in count: count[res_n] += 1
        # print(count)
        return count


    def eval_status(self, answer):
        prompt = eval_score_prompt.format(Question=self.data, ReferenceAnswer=self.ans_gt, CandidateAnswer=answer)
        res = (gpt(prompt)[0]).lower()
        print(res)
        
        # pattern = r'<Score>(.*?)</Score>'
        pattern = r'<(?:Score|Score1)>(.*?)</(?:Score|Score1)>'
        match = re.search(pattern, res, flags=re.IGNORECASE | re.DOTALL)

        if match:
            score_value = match.group(1)
            print(score_value)
            try:
                score = float(score_value)
            except ValueError:
                score = 0
        else:
            score = 0

        return score
    
    def render_gt_board(self):
        s = "GT Board:\n"
        for i in range(5):
            s += ' '.join(self.board_gt[i*5:(i+1)*5]) + '\n'
        return s
    
    def render_board(self):
        s = "Current Board:\n"
        for i in range(5):
            s += ''.join(self.board[i*5:(i+1)*5]) + '\n'
        return s

    def render_clues(self, status=None):
        s = ""
        # s += "Horizontal:\n"
        for i in range(5):
            if status is None or self.status[i] == status:
                s += 'h' + str(i+1) + '. ' + self.data[i] + '\n'
        # s += "Vertical:\n"
        for i in range(5, 10):
            if status is None or self.status[i] == status:
                s += 'v' + str(i-5+1) + '. ' + self.data[i] + '\n'
        return s
    
    def render_ans(self, status=None):
        s = ""
        # s += "Horizontal:\n"
        for i in range(5):
            if status is None or self.status[i] == status:
                s += 'h' + str(i+1) + '. ' + self.data[i] + ': ' + self.ans[i] + '\n'
        # s += "Vertical:\n"
        for i in range(5, 10):
            if status is None or self.status[i] == status:
                s += 'v' + str(i-5+1) + '. ' + self.data[i] + ': ' + self.ans[i] + '\n'
        return s
    
    def render_gt_ans(self, status=None):
        s = ""
        # s += "Horizontal:\n"
        for i in range(5):
            if status is None or self.status[i] == status:
                s += 'h' + str(i+1) + '. ' + self.data[i] + ': ' + self.ans_gt[i] + '\n'
        # s += "Vertical:\n"
        for i in range(5, 10):
            if status is None or self.status[i] == status:
                s += 'v' + str(i-5+1) + '. ' + self.data[i] + ': ' + self.ans_gt[i] + '\n'
        return s

    def render(self, status=True):
        if status:
            return "Current Decomposition:\n" + self.decomp #+ '\nUnfilled:\n' + self.render_ans(status=0) + '\nFilled:\n' + self.render_ans(status=1) + '\nChanged:\n' + self.render_ans(status=2)
        # else:
        #     return self.render_board() + '\n' + self.render_ans()
    
    def get_ans(self, board):
        ans = [''] * 10
        for i in range(5):
            ans[i] = ''.join(board[i*5:(i+1)*5])
        for i in range(5):
            ans[i+5] = ''.join(board[i::5])
        return ans
    
    def step(self, action):
        self.steps += 1
        print('steps:', self.steps)
        self.decomp = action
        return self.render()#, (self.steps >= 20)


class StrategyQATask(Task):
    """
    Input (x)   : a question
    Output (y)  : a decomposition into subquestions of the input question
    Reward (r)  : # TODO
    Input Example: 
    Output Example: 
    """
    def __init__(self, file='strategyqa_train.json'):
        """
        file: a text file, each line is some sentences
        """
        super().__init__()
        path = os.path.join(DATA_PATH, 'strategy_qa', file)
        self.data = json.load(open(path))
        self.steps = 2
        self.stops = ['\n'] * 2

    def __len__(self) -> int:
        return len(self.data)
    
    def get_input(self, idx: int) -> str:
        return self.data[idx]["question"]

    def get_facts(self, idx: int) -> str:
        # return self.data[idx]['facts']
        return []

    def get_answer(self, idx: int) -> str:
        return self.data[idx]['answer']

    def eval_status(self, answer, idx):
        prompt = eval_score_prompt.format(Question=self.get_input(idx), ReferenceAnswer=self.get_answer(idx), CandidateAnswer=answer)
        res = (gpt(prompt)[0]).lower()
        print(res)
        
        # pattern = r'<Score>(.*?)</Score>'
        pattern = r'<(?:Score|Score1)>(.*?)</(?:Score|Score1)>'
        match = re.search(pattern, res, flags=re.IGNORECASE | re.DOTALL)
        
        if match:
            score_value = match.group(1)
            print(score_value)
            try:
                score = float(score_value)
            except ValueError:
                score = 0
        else:
            score = 0
            
        return score

    @staticmethod
    def standard_prompt_wrap(f, x: str, y:str='') -> str:
        return standard_prompt.format(facts=f, input=x) + y

    @staticmethod
    def cot_prompt_wrap(f, x: str, y:str='') -> str:
        return cot_prompt.format(facts=f, input=x) + y

    @staticmethod
    def propose_prompt_wrap(x: str, y: str='') -> str:
        # current_question = get_current_question(y if y else x) 
        if y:
            prompt = propose_prompt_deep.format(input=y)
        else:
            prompt = propose_prompt.format(input=x) # in the first step the input will be a random sample from the data (original question), in the next steps it will be one of the output candidates from the previous step
        return prompt

    @staticmethod
    def vote_prompt_wrap(x: str, ys: list) -> str:
        # current_question = get_current_question(x) 
        prompt = vote_prompt.format(original_question=x) # add to the vote prompt the original question so that the outputs can be voted accordingly 
        prompt += 'Analyse each choice in detail, then conclude in the last line "The best choice is {s}", where s the integer id of the choice.\n'
        
        for i, y in enumerate(ys, 1): # for all porposals for future steps (in a list)
            # y = y.replace('Plan:\n', '')
            # TODO: truncate the plan part?
            prompt += f'Choice {i}:\n{y}\n' # appends the choice index and its corresponding text to the vote prompt
        return prompt # includes the original vote_prompt and the formatted choices based on the elements in the list of proposals for future steps
    
    @staticmethod
    def vote_outputs_unwrap(vote_outputs: list, n_candidates: int) -> list:
        vote_results = [0] * n_candidates # this list will be used to store the count of votes for each candidate
        for vote_output in vote_outputs:
            pattern = r".*best choice is .*(\d+).*" # extract the index of the best choice from the vote_output
            match = re.match(pattern, vote_output, re.DOTALL)
            if match:
                vote = int(match.groups()[0]) - 1 # extract the matched digits, convert them to an integer, subtract 1 (assuming 1-based indexing)
                if vote in range(n_candidates):
                    vote_results[vote] += 1
            else:
                print(f'vote no match: {[vote_output]}')
        return vote_results # contains the count of votes for each candidate

    @staticmethod
    def answer_prompt_wrap(x: str, ys: str) -> str:
        prompt = answer_prompt.format(original_question=x, decomposition=ys)
        return prompt