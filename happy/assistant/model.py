from happy.env import Keys
from happy.assistant.llm import CohereLLM
from prompts.model import prompt, FixedHistory, ExampleChatHistory

class Model:
    funcs = ["general","realtime","open", "camera", "close", "play","generate image","content","google search","youtube search"]
    def __init__(self) -> None:
        self.messages = ExampleChatHistory.copy()
        self.llm = CohereLLM(
            model = "command-r-plus",
            temperature = 0.7,
            system_prompt = prompt,
            max_tokens = 2048,
            messages=FixedHistory+self.messages,
            api_key=Keys["Cohere"]
        )
    def filter(self, response:str) -> str:
        response = response.replace("\n", "")
        return response
    
    def extract(self, response:str) -> list[str]:
        response = response.split(",")
        response = [i.strip() for i in response]
        temp = []
        for task in response:
            for func in self.funcs:
                if task.startswith(func):
                    temp.append(task)
        return temp

    def run(self, prompt: str) -> list[str]:
        response = self.llm.run(prompt)
        self.messages.append({"role": "User","message": f"{prompt}"})
        self.messages.append({"role": "Chatbot", "message": response})
        self.llm.messages = self.messages[-12:]
        
        response = self.filter(response)
        response = self.extract(response)
        return response


if __name__ == "__main__":
    model = Model()
    print(model.run("Hello, how are you?"))
    print(model.run("Hello, how are you?"))
    print(model.run("Hello, how are you?"))




