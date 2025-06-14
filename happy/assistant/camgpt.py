from happy.env import Keys
from happy.logging import Logger
from prompts.camgpt import prompt, prompt_required
from datetime import datetime
from nara.llm._openai import OpenAI, GPT4OMINI, Role

l = Logger(__file__)

class CamGPTModel:
    required = prompt_required
    def __init__(self, details: dict) -> None:
        try:
            self.system_prompt = prompt.format(**details)
        except Exception as e:
            l.error(e)

        self.llm = OpenAI(
            model = GPT4OMINI,
            temperature = 0.7,
            systemPrompt = self.system_prompt,
            maxTokens = 4096,
            apiKey=Keys["OpenAI"]
        )
    
    def dateTime(self) -> str:
        date_time_=f"Please use this realtime information if needed,\nCurrent date and time: {datetime.now()}"
        return date_time_

    def run(self, prompt: str, messages: list, imagebase64: str) -> str:
        self.llm.messages = [{"role": "system", "content": self.system_prompt}] + messages + [{"role": "system", "content": self.dateTime()}]
        self.llm.addMessage(Role.user, content=prompt+" (tell me in detail)", imageUrl=f"{imagebase64}")
        response = self.llm.run()
        return response