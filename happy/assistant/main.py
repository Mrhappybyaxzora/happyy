from happy.assistant import (
    CamGPTModel,
    ChatModel,
    Model,
    RealtimeModel,
    # TextToSpeechBytes,
    wopen,
    Content,
    generate_images,
    playonyt,
    create_content_url,
)
from happy.assistant.voice import TextToSpeechBytes
from happy.assistant.llm.gemini import Gemini, GEMINI_1_5_FLASH
from happy.database import User
from rich import print
import asyncio
import base64
from dataclasses import dataclass, asdict
from typing import Union
from mtranslate import translate

@dataclass
class Response:
    text: str
    wopens: list[str]
    plays: list[str]
    images: list[str]
    contents: list[str]
    googlesearches: list[str]
    youtubesearches: list[str]
    cam: Union[bool, None, str] = None
    audiobase64: str | None = None
    def asdict(self):
        return asdict(self)




class Assistant:
    def __init__(self, user: dict, history: list):
        self.user = user
        self.input_language = user.get("InputLanguage", "en-US")
        
        cam_required = CamGPTModel.required
        chat_required = ChatModel.required
        realtime_required = RealtimeModel.required

        self.cam = CamGPTModel({key: user[key] for key in cam_required if key in user})
        self.chat = ChatModel({key: user[key] for key in chat_required if key in user})
        self.realtime = RealtimeModel({key: user[key] for key in realtime_required if key in user})
        self.model = Model()
        self.file_model = Gemini(GEMINI_1_5_FLASH)

        self.history = history

    
    async def inactive_query(self, history: list):
        print("Inactive query")
        generate_q = self.chat.run("System: User is inactive. Generate short querie that the user might be interested in. and ask them. DO NOT MENTION ANYTHING JUST ASK THE QUESTION.", 
                                   history)
        byte_data = await TextToSpeechBytes(generate_q)
        
        base64_encoded = base64.b64encode(byte_data).decode('utf-8')
        return Response(text=generate_q, wopens=[], plays=[], images=[], contents=[], googlesearches=[], youtubesearches=[], audiobase64=base64_encoded)
    
    async def run(self, prompt: str, imgbase64: str, files: list, history: list):
        response = Response(text="", wopens=[], plays=[], images=[], contents=[], googlesearches=[], youtubesearches=[])
        print("prompt = ", prompt)
        print("imgbase64 = ", imgbase64[:100] if imgbase64 else None)
        if "TTCAMTOKENTT".lower() in prompt.lower():
            print("cam token found")
            if self.input_language != "en-US":
                prompt = translate(prompt[11:], self.input_language)
            async def cam_task():
                try:
                    resp = await asyncio.to_thread(self.cam.run, prompt, history, imgbase64)
                    byte_data = await TextToSpeechBytes(resp)
                    base64_encoded = base64.b64encode(byte_data).decode('utf-8')
                    response.audiobase64 = base64_encoded
                    response.text = resp
                except Exception as e:
                    response.text = f"Error processing camera request: {str(e)}"
            await cam_task()
            return response

        if prompt.lower() == "[user is inactive]":
            return await self.inactive_query(history)
        if self.input_language != "en-US":
            prompt = translate(prompt)
        decision = self.model.run(prompt)
        print(f"Decision: {decision}")

        g = any([i for i in decision if i.startswith("general")])
        r = any([i for i in decision if i.startswith("realtime")])
        mearged_q = " and ".join(
            [" ".join(i.split()[1:]) for i in decision if i.startswith("general") or i.startswith("realtime")]
        )

        tasks = []

        if imgbase64 and (g or r):
            async def cam_task():
                resp = await asyncio.to_thread(self.cam.run, mearged_q, history, imgbase64)
                byte_data = await TextToSpeechBytes(resp)
                base64_encoded = base64.b64encode(byte_data).decode('utf-8')
                response.audiobase64 = base64_encoded
                response.text = resp

            tasks.append(cam_task())
        elif g or r:
            if g and r or r:
                async def realtime_task():
                    # TODO: Fix realtime q parameter. 
                    resp = await asyncio.to_thread(self.realtime.run, mearged_q, history)
                    byte_data = await TextToSpeechBytes(resp)
                    base64_encoded = base64.b64encode(byte_data).decode('utf-8')
                    response.audiobase64 = base64_encoded
                    response.text = resp

                tasks.append(realtime_task())
            else:
                async def chat_task():
                    try:
                        if files:
                            self.file_model.messages = self.chat.llm.messages + history
                            resp = await asyncio.to_thread(self.file_model.run, mearged_q, files = files)
                        else:
                            resp = await asyncio.to_thread(self.chat.run, mearged_q, history)
                            if not isinstance(resp, str):
                                resp = str(resp)
                        try:
                            byte_data = await TextToSpeechBytes(resp)
                            base64_encoded = base64.b64encode(byte_data).decode('utf-8')
                            response.audiobase64 = base64_encoded
                        except Exception as e:
                            print(f"Text to speech error: {str(e)}")
                            response.audiobase64 = None
                        response.text = resp
                    except Exception as e:
                        error_msg = str(e) if isinstance(e, Exception) else "Unknown error occurred"
                        response.text = f"Error processing chat request: {error_msg}"
                        print(f"Chat error: {error_msg}")

                tasks.append(chat_task())

        funcs = ["open", "play", "camera", "close", "generate image", "content", "google search", "youtube search"]
        funcused = [i for i in decision if any([i.startswith(j) for j in funcs])]

        for fun_ in funcused:
            fun = f"{fun_}"
            print(f"{fun = }") 
            isst = fun.startswith
            if fun == "open webcam":
                response.cam = True
            elif fun == "close webcam":
                response.cam = False
            
            elif isst("camera"):
                if imgbase64:
                    async def cam_task(w:str):
                        resp = await asyncio.to_thread(self.cam.run, w, history, imgbase64)
                        byte_data = await TextToSpeechBytes(resp)
                        base64_encoded = base64.b64encode(byte_data).decode('utf-8')
                        response.audiobase64 = base64_encoded
                        response.text = resp

                    tasks.append(cam_task(fun[7:]))
                    
                else:
                    response.cam = f"{fun[7:]}"
            
            elif isst("open"):
                async def wopen_task(whattoopen: str):
                    print("opened_for", whattoopen)
                    resp = await asyncio.to_thread(wopen, whattoopen)
                    response.wopens.append(resp)

                tasks.append(wopen_task(fun[5:]))
            elif isst("play"):
                async def play_task(whattoplay: str):
                    resp = await asyncio.to_thread(playonyt, whattoplay)
                    response.plays.append(resp)

                tasks.append(play_task(fun[5:]))
            elif isst("generate image"):
                async def image_task(imageofwhat: str):
                    resp = await generate_images(imageofwhat)
                    if len(resp) > 0:
                        base64_image = resp[0]
                        def create_image_url(base64_image):
                            return "data:image/png;base64," + base64_image

                        resp = create_image_url(base64_image)

                        response.images.append(resp)

                tasks.append(image_task(fun[12:]))
            elif isst("content"):
                async def content_task(contentofwhat: str):
                    resp = await asyncio.to_thread(Content, contentofwhat)
                    resp = "/notepad" + create_content_url(resp)
                    response.contents.append(resp)
                tasks.append(content_task(fun[7:]))
            elif isst("google search"):
                response.googlesearches.append("https://www.google.com/search?q=" + fun[11:])
            elif isst("youtube search"):
                response.youtubesearches.append('https://www.youtube.com/results?search_query=' + fun[13:])

        await asyncio.gather(*tasks)
        return response


if __name__ == "__main__":
    user = User(
        _id="a",
        FullName="a",
        Age=0,
        Email="a",
        Address="a",
        Gender="a",
        DOB="a",
        Height="a",
        InputLanguage="a",
        AssistantVoice="a",
        ContactNumber="a",
        Password="a",
        CreatedAt="a"
    ).to_dict()

    assistant = Assistant(user, [])

    while True:
        prompt = input(">>> ")
        history = []
        resp = asyncio.run(assistant.run(prompt, None, history))
        print(resp)
