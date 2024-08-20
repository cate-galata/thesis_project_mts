# Bachelor Thesis Project: Tree-Structured Strategic Problem Solving with Large Language Models
This repository contains the code and resources for my bachelor thesis project, which I conducted in collaboraiton with the Research Group of Social Computing of the Technical University of Munich. The project explores innovative methods for enhancing problem-solving capabilities in AI by leveraging tree structures in combination with large language models (LLMs).

## Overview
The primary goal of this thesis is to develop a framework that utilizes tree-structured strategies to improve the reasoning abilities of LLMs in complex problem-solving tasks. Inspired by issue trees, a widely employed technique for strategic problem-solving in the management domain, this thesis presents a novel LLM reasoning approach, Multi Tree Search (MTS). By structuring problems as trees, the project aims to systematically decompose and address sub-problems, leading to more accurate and interpretable solutions.

## Features
Tree Structure Framework: Implementation of a tree-based approach for problem decomposition and solution synthesis.
Large Language Model Integration: Utilization of a state-of-the-art LLM to handle natural language processing and reasoning tasks.
Case Studies and Experiments: Comprehensive analysis and evaluation of the framework on 3 datasets requiring commonsense intuition and engaging in logical reasoning
- StrategyQA: diverse implicit questions that require strategic inference to solve, allowing for multiple valid reasoning chains,
- GSM8k: grade school math problems requiring the construction of logical mathematical solution strategies from natural language descriptions,
- Researchy Questions: non-factoid, multi-perspective questions that require complex reasoning and information analysis to be solved.

## Contents
**src/tot:** Contains the source code for the framework and algorithms. 
  **data/:** Includes datasets used for testing.
  **prompts/:** Includes prompts for the LLM.
  **tasks/:** Includes the implementation of classes for all datasets.
**scripts/:** Scripts for running tree decomposition experiments and analyzing results.
**logs/:** Documentation of results.

## Getting Started
1. Set up OpenAI API key and add it in the place of 'PUT-YOUR-KEY-HERE' in the models.py file of the src/tot folder.

2. Download the StrategyQA, GSM8k and Researchy Question datasets and add them to the respective folders under src/tot/data. For StrategyQA download the [training data](https://github.com/eladsegal/strategyqa/blob/main/data/strategyqa/train.json), for GSM8k download the [training data](https://github.com/openai/grade-school-math/blob/master/grade_school_math/data/train.jsonl) and for Researchy Questions download the [test data](https://huggingface.co/datasets/corbyrosset/researchy_questions/viewer/default/test).
