from happy.env import Keys
from happy.logging import Logger
from happy.assistant.llm import OpenAILLM
from prompts.realtime import prompt, prompt_required
from datetime import datetime
from googlesearch import search

l = Logger(__file__)

class RealtimeModel:
    required = prompt_required
    def __init__(self, details: dict) -> None:
        try:
            self.system_prompt = prompt.format(**details)
        except Exception as e:
            l.error(e)

        self.llm = OpenAILLM(
            model = "gpt-3.5-turbo",
            temperature = 0.7,
            system_prompt = self.system_prompt,
            max_tokens = 4096,
            api_key=Keys["OpenAI"]
        )
    
    def dateTime(self) -> str:
        date_time_=f"Please use this realtime information if needed,\nCurrent date and time: {datetime.now()}"
        return date_time_

    def GoogleSearch(self, query: str) -> str:
        results = list(search( query, advanced = True, num_results= 5 ))
        Answer =f"The search results for '{query}'are : \n[start]\n"

        for i in results:
            Answer += f"Title : {i.title}\nDiscription : {i.description}\n\n"

        Answer += "[end]"
        return Answer

    def run(self, prompt: str, messages: list, q: str|None = None) -> str:
        self.llm.messages = [{"role": "system", "content": self.system_prompt}]+messages
        
        self.llm.add_message(self.llm.SYSTEM, self.GoogleSearch(prompt))
        self.llm.add_message(self.llm.SYSTEM, self.dateTime())

        response = self.llm.run(prompt)
        
        return response
    
    



