def get_task(name):
    if name == 'strategyQA':
        from tot.tasks.strategy_qa import StrategyQATask
        return StrategyQATask()
    elif name == 'researchy':
        from tot.tasks.researchy import ResearchyTask
        return ResearchyTask()
    elif name == 'gsm8k':
        from tot.tasks.gsm8k import GSM8KTask
        return GSM8KTask()
    else:
        raise NotImplementedError