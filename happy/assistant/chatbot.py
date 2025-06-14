from happy.env import Keys
from happy.logging import Logger
from happy.assistant.llm import OpenAILLM
from prompts.chatbot import prompt, prompt_required
from datetime import datetime

l = Logger(__file__)

class ChatModel:
    required = prompt_required
    def __init__(self, details: dict) -> None:
        try:
            # Check if all required fields are present
            missing_fields = self.required - set(details.keys())
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
            
            self.system_prompt = prompt.format(**details)
        except Exception as e:
            l.error(f"Error initializing ChatModel: {str(e)}")
            # Provide a default system prompt if initialization fails
            self.system_prompt = "You are Mr.Happy, a friendly and advanced AI Assistant. Be humorous and helpful."

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

    def run(self, prompt: str, messages: list) -> str:
        try:
            self.llm.messages = [{"role": "system", "content": self.system_prompt}]+messages
            self.llm.add_message(self.llm.SYSTEM, self.dateTime())

            response = self.llm.run(prompt)
            if not isinstance(response, str):
                response = str(response)
            return response
        except Exception as e:
            error_msg = str(e) if isinstance(e, Exception) else "Unknown error occurred"
            l.error(f"Error in ChatModel.run: {error_msg}")
            return f"I apologize, but I encountered an error: {error_msg}"
    
    
        