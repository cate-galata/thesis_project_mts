import itertools
import numpy as np
from functools import partial
from tot.models import gpt

def get_value(task, x, y, n_evaluate_sample, cache_value=True):
    value_prompt = task.value_prompt_wrap(x, y)
    if cache_value and value_prompt in task.value_cache:
        return task.value_cache[value_prompt]
    value_outputs = gpt(value_prompt, n=n_evaluate_sample, stop=None)
    value = task.value_outputs_unwrap(x, y, value_outputs)
    if cache_value:
        task.value_cache[value_prompt] = value
    return value

def get_values(task, x, ys, n_evaluate_sample, cache_value=True):
    values = []
    local_value_cache = {}
    for y in ys:  # each partial output
        if y in local_value_cache:  # avoid duplicate candidates
            value = 0
        else:    
            value = get_value(task, x, y, n_evaluate_sample, cache_value=cache_value)
            local_value_cache[y] = value
        values.append(value)
    return values

def get_votes(task, x, ys, n_evaluate_sample):
    vote_prompt = task.vote_prompt_wrap(x, ys)
    print('vote_prompt: '+vote_prompt)
    vote_outputs = gpt(vote_prompt, n=n_evaluate_sample, stop=None)
    print(vote_outputs)
    values = task.vote_outputs_unwrap(vote_outputs, len(ys))
    print(values)
    return values

def get_proposals(task, x, y, n_generate_sample): 
    propose_prompt = task.propose_prompt_wrap(x, y)
    print('propose_prompt: '+propose_prompt)
    proposals = gpt(propose_prompt, n=n_generate_sample, stop=None)#[0].split('\n\n') 
    print(proposals)
    # return [y + _ + '\n' for _ in proposals]
    return [elem for item in proposals for elem in (item.split('\n\n') if '\n\n' in item else [item])]

def get_samples(task, f, x, y, n_generate_sample, prompt_sample, stop):
    if prompt_sample == 'standard':
        prompt = task.standard_prompt_wrap(f, x, y)
    elif prompt_sample == 'cot':
        prompt = task.cot_prompt_wrap(f, x, y)
        print('prompt: '+prompt)
    else:
        raise ValueError(f'prompt_sample {prompt_sample} not recognized')
    # print(prompt)
    samples = gpt(prompt, n=n_generate_sample, stop=stop)
    print('samples: ')
    print(samples)
    return [y + _ for _ in samples]

def get_answer(task, x, ys):
    answer_prompt = task.answer_prompt_wrap(x, ys)
    print('answer prompt: ' + answer_prompt)
    answer = gpt(answer_prompt, n=1, stop=None)
    print("and the answer is: "+str(answer))
    return answer

def solve(args, task, idx, to_print=True):
    global gpt
    gpt = partial(gpt, model=args.backend, temperature=args.temperature)
    print(gpt)

    x = task.get_input(idx)  # selects a random sample from the data as the input
    ys = ['']  # current output candidates
    infos = []
    for step in range(task.steps):
        # generation
        if args.method_generate == 'sample':
            new_ys = [get_samples(task, x, y, args.n_generate_sample, prompt_sample=args.prompt_sample, stop=task.stops[step]) for y in ys]
        elif args.method_generate == 'propose':
            new_ys = [get_proposals(task, x, y, args.n_generate_sample) for y in ys] # make a list of the proposals for future steps for all output candidates of the previous step, ys only contains one element because b=1
        new_ys = list(itertools.chain(*new_ys))
        print('new_ys: ')
        print(new_ys)
        ids = list(range(len(new_ys)))
        # evaluation
        if args.method_evaluate == 'vote':
            values = get_votes(task, x, new_ys, args.n_evaluate_sample) # get votes for all proposals for future steps (previous list)
        elif args.method_evaluate == 'value':
            values = get_values(task, x, new_ys, args.n_evaluate_sample)

        # selection
        if args.method_select == 'sample':
            ps = np.array(values) / sum(values)
            select_ids = np.random.choice(ids, size=args.n_select_sample, p=ps).tolist()
        elif args.method_select == 'greedy':
            select_ids = sorted(ids, key=lambda x: values[x], reverse=True)[:args.n_select_sample] 
            print('select_ids: ')
            print(select_ids)
        select_new_ys = [new_ys[select_id] for select_id in select_ids] # select the b best proposals for the future steps

        # log
        if to_print: 
            sorted_new_ys, sorted_values = zip(*sorted(zip(new_ys, values), key=lambda x: x[1], reverse=True))
            print(f'-- new_ys --: {sorted_new_ys}\n-- sol values --: {sorted_values}\n-- choices --: {select_new_ys}\n')
        
        infos.append({'step': step, 'x': x, 'ys': ys, 'new_ys': new_ys, 'values': values, 'select_new_ys': select_new_ys})
        ys = select_new_ys
    
    ans = get_answer(task, x, ys)
    if to_print: 
        print(ys + ans)
    return ys, ans, {'steps': infos}

def naive_solve(args, task, idx, to_print=True):
    global gpt
    gpt = partial(gpt, model=args.backend, temperature=args.temperature)
    # print(gpt)
    x = task.get_input(idx)  # input
    f = task.get_facts(idx)
    ys = get_samples(task, f, x, '', args.n_generate_sample, args.prompt_sample, stop=None)
    score = task.eval_status(ys, idx) 
    return ys, {}, score