from happy.env import Keys
from groq import Groq
from happy.logging import Logger

l = Logger(__file__)

def Content(Topic) -> str:
    try:
        client = Groq(api_key=Keys["Groq"])
        def ContentWriterAI(prompt):
            SystemChatBot = [{"role": "system","content": f"Hello, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]
            messages = []
            messages.append({"role": "user", "content": f"{prompt}"})
            completion = client.chat.completions.create(
            model = "mixtral-8x7b-32768",
            messages = SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None)

            Answer =""
            for chunk in completion:
                    if chunk.choices[0].delta.content:
                        Answer += chunk.choices[0].delta.content

            Answer = Answer.replace("</s>", "")
            return Answer

        try:
            ContentByAI = ContentWriterAI(Topic)
            if not ContentByAI:
                return "I apologize, but I couldn't generate the content. Please try again."
            return ContentByAI
        except Exception as e:
            error_msg = str(e) if isinstance(e, Exception) else "Unknown error occurred"
            l.error(f"Content generation error: {error_msg}")
            return f"I apologize, but I encountered an error while generating the content: {error_msg}"
    except Exception as e:
        error_msg = str(e) if isinstance(e, Exception) else "Unknown error occurred"
        l.error(f"Groq client initialization error: {error_msg}")
        return f"I apologize, but I couldn't initialize the content generation service: {error_msg}"