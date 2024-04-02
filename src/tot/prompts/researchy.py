### NAIVE ###
standard_prompt = '''{input}'''

cot_prompt = '''Solve this question step by step and show your work: "{input}".'''

### DFS ###
propose_prompt = '''If the input is a question, output its best decomposition into subquestions. These subquestions will be used to retrieve information to answer the input question, so they should be able to retrieve all the information needed without any overlaps between them.
Example:
Input: How does public transport help the economy?
Answer:
How does public transport help the economy?
- What is public transport?
- What are the direct economic benefits of public transport?
- What are the indirect economic benefits of public transport?
- How do the economic benefits of public transport compare to the costs of providing and maintaining public transport?

If the input is a question decomposition, enhance it by adding subquestions to subquestions only when you still need more information to answer the original question. Subquestions of subquestions are represented as lines following their originator, prefixed by a tab and a hyphen.
Example:
Input: How does public transport help the economy?
Answer:
How does public transport help the economy?
- What is public transport?
    - What are the different types of public transport?
    - How many people use public transport in different regions or countries?
- What are the direct economic benefits of public transport?
    - How public transport reduces costs for users e.g. fuel, parking, maintenance, etc.?
    - How does public transport generate revenue?
- What are the indirect economic benefits of public transport?
    - How does public transport reduce congestion?
    - How does public transport increase access to education, employment, health?
    - How does public transport enhance productivity and innovation?
    - How does public transport contribute to environmental and social goals?
- How do the economic benefits of public transport compare to the costs of providing and maintaining public transport?
    - What are the main costs of public transport?
    - How are the costs of public transport financed?
    - How are the benefits and costs of public transport measured and evaluated?

Structure your output exaclty like in the examples.
Also output your confidence level for the entire decomposition at the end choosing one from (certain/high/medium/low), like this: confidence level: (certain/high/medium/low). 
Use "certain" cautiously and only when you are absolutely sure this is the optimal decomposition (i.e. all subquestions are mutually exclusive, collectively exhaustive and relevant to answer the question they originate from).
Avoid further decomposition when the existing questions already provide sufficient information to extrapolate the answer. 
If all necessary information to answer the question has been found and thus no further decomposition into subquestions is needed, output: confidence level: stop.

Input: {input}
'''


value_prompt = '''Output how likely the current decomposition into subquestions is to answer the original question. Assess if all subquestions can be answered solely with information from your knowledge, and if they contribute relevant information. Output sure/maybe/impossible in the last line. Output sure for relevant, mutually exclusive, and collectively exhaustive subquestions. Output impossible if no information from your knowledge can answer a question.
{input}
'''


answer_prompt = '''Given a question decomposition, use it to help you find the answer to the follwing problem: "{original_question}". Respond to each subquestion in the decomposition individually then aggregate the answers to derive the solution to the problem. 
Input:
- What battery does a Toyota Prius use? 
    - What material is the Toyota Prius battery made of?
    - What is the melting point of the material of a Toyota Prius battery?
- What is the maximum temperature a microwave can reach?
Output:
- What battery does a Toyota Prius use? A Toyota Prius uses a 202 V nickel-metal hydride battery.
    - What material is the Toyota Prius battery made of? Nickel
    - What is the melting point of the material of a Toyota Prius battery? Nickel has a melting point of 2651 F
- What is the maximum temperature a microwave can reach? Microwaves rarely warm food more than 212 F.
Answer: Can a microwave melt a Toyota Prius battery? false

Input: 
{decomposition}
Output:
'''


### BFS ###
propose_prompt_bfs = '''You will get a question as input. Your task is to decompose the question into a minimal number of subquestions 
which are needed to gather information and answer the question. These subquestions will form the first layer of a tree 
decomposition of the question. These subquestions can be further decomposed in future steps so don't go into so much detail 
in the first decoposition step, focus on gathering the main information you need to answer the question.

Input: Is a Boeing 737 cost covered by Wonder Woman (2017 film) box office receipts?
Output:
Is a Boeing 737 cost covered by Wonder Woman (2017 film) box office receipts?
- How much does a Boeing 737 cost?
- How much did the 2017 movie Wonder Woman gross?
- Is #1 less than #2?

Input: {input}
Output:
'''


propose_prompt_deep = '''You will get a decomposition of a question into subquestions which help answer it as input.
Your task is to refine the decomposition by decomposing subquestions further if you require additional information. 
Subquestions of subquestions are represented as separate lines in the decomposition which come
after their originator question and are preceded by a tab and a hyphen. Do not decompose subquestions whose answer you 
already know. If you do not require any additional decompositions and are able to answer all questions output the unchanged previous decomposition followed by "STOP".

Input:
Is a Boeing 737 cost covered by Wonder Woman (2017 film) box office receipts?
- How much money did the movie Wonder Woman gross? 
- Is #1 more than the price of a Boeing 737?
Output:
Is a Boeing 737 cost covered by Wonder Woman (2017 film) box office receipts?
- How much money did the movie Wonder Woman gross? 
- Is #1 more than the price of a Boeing 737? 
    - How much does a Boeing 737 cost?

Input: 
{input}
Output:
'''


vote_prompt = ''''Given a question: "{original_question}" and several choices for a layer of a tree decomposition into 
subquestions which will help answer it, decide which choice is most promising. Simplicity is key: don't vote for 
decompositions which over-analyze the question and repeat subquestions which retrieve similar information.
'''


answer_prompt_bfs = '''You will get a decompsition of a question into subquestions as input. Your task is to use that decomposition 
to answer the question "{original_question}". Answer each subquestion separately and then aggregate tha answers to find the 
answer to the question. 

Input:
Is a Boeing 737 cost covered by Wonder Woman (2017 film) box office receipts?
- How much money did the movie Wonder Woman gross? 
- Is #1 more than the price of a Boeing 737? 
    - How much does a Boeing 737 cost?
Output:
Is a Boeing 737 cost covered by Wonder Woman (2017 film) box office receipts? true
- How much money did the movie Wonder Woman gross? 800 million dollars
- Is #1 more than the price of a Boeing 737? true
    - How much does a Boeing 737 cost? 1.6 million dollars

Input: 
{decomposition}
Output:
'''