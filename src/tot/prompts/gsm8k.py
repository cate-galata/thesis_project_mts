### NAIVE ###
standard_prompt = '''
Input: Roger has 5 tennis balls. He buys 2 more cans of tennis balls. Each can has 3 tennis balls. How many tennis balls does he have now?
Answer: The answer is 11.
Input: The cafeteria had 23 apples. If they used 20 to make lunch and bought 6 more, how many apples do they have?
Answer: The answer is 9.
Input: Tracy used a piece of wire 4 feet long to support tomato plants in the garden. The wire was cut into pieces 6 inches long. How many pieces did she obtain?
Answer: The answer is 8.
Input: Tom's ship can travel at 10 miles per hour. He is sailing from 1 to 4 PM. He then travels back at a rate of 6 mph. How long does it take him to get back?
Answer: The answer is 5.
Input: There are four schools competing at a basketball tournament. Each school has sent a girls’ basketball team and a boys’ basketball team and each team has 5 players each. Each school has also sent a coach for each team. In total, how many people have all of the schools sent?
Answer: The answer is 48.
Input: {input}
'''


cot_prompt = '''
Input: Roger has 5 tennis balls. He buys 2 more cans of tennis balls. Each can has 3 tennis balls. How many tennis balls does he have now?
Answer: Roger started with 5 balls. 2 cans of 3 tennis balls each is 6 tennis balls. 5 + 6 = 11. The answer is 11.
Input: The cafeteria had 23 apples. If they used 20 to make lunch and bought 6 more, how many apples do they have?
Answer: The cafeteria had 23 apples originally. They used 20 to make lunch. So they had 23 - 20 = 3. They bought 6 more apples, so they have 3 + 6 = 9. The answer is 9.
Input: Tracy used a piece of wire 4 feet long to support tomato plants in the garden. The wire was cut into pieces 6 inches long. How many pieces did she obtain?
Answer: The wire was 4 feet long. This means it was 4 * 12 = 48 inches long. It was cut into pieces 6 inches long. This means she obtained 48 / 6 = 8 pieces. The answer is 8.
Input: Tom's ship can travel at 10 miles per hour. He is sailing from 1 to 4 PM. He then travels back at a rate of 6 mph. How long does it take him to get back?
Answer: He travels at 10 mph from 1 to 4 PM. This means he travels 3 hours. 3 hours at 10 mph means he travels 3 * 10 = 30 miles. He then travels back at 6 mph. This means he travels 6 miles per hour. He has to travel 30 miles, so it takes him 30 / 6 = 5 hours. The answer is 5. 
Input: There are four schools competing at a basketball tournament. Each school has sent a girls’ basketball team and a boys’ basketball team and each team has 5 players each. Each school has also sent a coach for each team. In total, how many people have all of the schools sent?
Answer: Each school has sent 2 teams, each with 5 players. This means each school has sent 2 * 5 = 10 players. Each school has also sent 2 coaches. This means each school has sent 10 + 2 = 12 people. There are 4 schools, so in total all of the schools have sent 4 * 12 = 48 people. The answer is 48.
Input: {input}
'''


### DFS ###
propose_prompt = '''If the input is a question, decompose it into a minimal set of subquestions essential for information gathering and answering. The subquestions form the first layer of a tree decomposition, with the potential for further decomposition in subsequent steps. Maintain a focus on extracting key information to answer the question.
Example:
Input: Each bird eats 12 beetles per day, each snake eats 3 birds per day, and each jaguar eats 5 snakes per day. If there are 6 jaguars in a forest, how many beetles are eaten each day? 
Output:
How many beetles are eaten each day?
- How many beetles are eaten per jaguar? (must be decomposed further)
- How many jaguars are there?

If the input is a question decomposition, enhance it by refining subquestions only when additional information from the problem description is necessary. Subquestions of subquestions are represented as lines following their originator, prefixed by a tab and a hyphen.
Example:
Input:
How many beetles are eaten each day?
- How many beetles are eaten per jaguar? (must be decomposed further)
- How many jaguars are there?
Output:
How many beetles are eaten each day?
- How many beetles are eaten per jaguar? 
    - How many beetles are eaten per snake?
    - How many snakes are eaten per jaguar?
- How many jaguars are there?

Structure your output exaclty like in the examples.
Also output your confidence level for the entire decomposition at the end choosing one from (certain/high/medium/low), like this: confidence level: (certain/high/medium/low). 
Use "certain" cautiously and only when you are absolutely sure this is the optimal decomposition (i.e. all subquestions are mutually exclusive, collectively exhaustive and relevant to answer the question they originate from).
Avoid further decomposition when the existing questions already provide sufficient information to extrapolate the answer. Do NOT add subquestions whose answers cannot be found in the problem description. 
If all necessary information to answer the question has been found and thus no further decomposition into subquestions is needed, output: confidence level: stop.

Input: {input}
'''


value_prompt = '''Output how likely the current decomposition into subquestions is to answer the original question. Assess if all subquestions can be answered solely with information from the problem description, and if they contribute relevant information. Output sure/maybe/impossible in the last line. Output sure for relevant, mutually exclusive, and collectively exhaustive subquestions. Output impossible if no information in the problem description can answer a question.
{input}
'''


answer_prompt = '''
Given a question decomposition, use it to help you find the answer to the follwing problem: "{original_question}".
Respond to each subquestion in the decomposition individually then aggregate the answers to derive the solution to their originator question. To aggregate answers decide which are the best mathematical operators to use between the different quantities based on the problem description.
ONLY use information from the problem description to answer any question. Output the final answer as the original question followed by a single number answer (no measurement units).

Input:
- How many beetles are eaten per jaguar? 
    - How many beetles are eaten per snake?
        - How many beetles are eaten per bird?
        - How many birds are eaten per snake?
    - How many snakes are eaten per jaguar?
- How many jaguars are there?
Output:
- How many beetles are eaten per jaguar? 180
    - How many beetles are eaten per snake? 36
        - How many beetles are eaten per bird? 12
        - How many birds are eaten per snake? 3
    - How many snakes are eaten per jaguar? 5
- How many jaguars are there? 6
Answer: How many beetles are eaten each day? 1080

Input: 
{decomposition}
Output:
'''


### BFS ###
propose_prompt_bfs = '''Decompose the given question into a minimal set of subquestions essential for information gathering and answering. The subquestions form the first layer of a tree decomposition, with the potential for further decomposition in subsequent steps. Maintain a focus on extracting key information to answer the question. Output two distinct decomposition possibilities for the input question.

Input: Each bird eats 12 beetles per day, each snake eats 3 birds per day, and each jaguar eats 5 snakes per day. If there are 6 jaguars in a forest, how many beetles are eaten each day? 
Output:
How many beetles are eaten each day?
- How many beetles are eaten per jaguar? 
- How many jaguars are there?

Input: {input}
Output:
'''


propose_prompt_deep = '''Enhance the given question decomposition by refining subquestions only when additional information from the problem description is necessary. Subquestions of subquestions are represented as lines following their originator question, prefixed by a tab and a hyphen.

Input:
How many beetles are eaten each day?
- How many beetles are eaten per jaguar? 
- How many jaguars are there?
Output:
How many beetles are eaten each day?
- How many beetles are eaten per jaguar? 
    - How many beetles are eaten per snake?
    - How many snakes are eaten per jaguar?
- How many jaguars are there?

Avoid further decomposition when the existing questions already provide sufficient information to answer. Do NOT add subquestions whose answers cannot be found in the input question text. Output "stop" if no additional decompositions should be added in this step like in the example:
Input:
How many beetles are eaten each day?
- How many beetles are eaten per jaguar? 
    - How many beetles are eaten per snake?
        - How many beetles are eaten per bird?
        - How many birds are eaten per snake?
    - How many snakes are eaten per jaguar?
- How many jaguars are there?
Output:
stop

Input: 
{input}
Output:
'''

vote_prompt = ''''Given a question: "{original_question}" and multiple choices for a tree decomposition into subquestions, select the most promising option. Prioritize simplicity by favoring decompositions with subquestions aiming to gather the minimal information needed to answer the question.'''


answer_prompt_bfs = '''
Given a question decomposition, use it to answer "{original_question}". Respond to each subquestion individually and aggregate the answers to derive the overall solution.

Input:
How many beetles are eaten each day?
- How many beetles are eaten per jaguar? 
    - How many beetles are eaten per snake?
        - How many beetles are eaten per bird?
        - How many birds are eaten per snake?
    - How many snakes are eaten per jaguar?
- How many jaguars are there?
Output:
How many beetles are eaten each day? 1080
- How many beetles are eaten per jaguar? 180
    - How many beetles are eaten per snake? 36
        - How many beetles are eaten per bird? 12
        - How many birds are eaten per snake? 3
    - How many snakes are eaten per jaguar? 5
- How many jaguars are there? 6
So the final answer is: 1080

Input: 
{decomposition}
Output:
'''