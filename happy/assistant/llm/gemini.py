import os

from abc import ABC, abstractmethod
from typing import Optional, Union, List, Dict, Any, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv
from pythonjsonlogger import jsonlogger

import logging
import os

load_dotenv()

class Role(Enum):
    system = "system"
    user = "user"
    assistant = "assistant"

class ModelType(Enum):
    textonly = "textonly"
    textandimage = "textandimage"
    textandfile = "textandfile"


@dataclass
class Model:
    name: str
    typeof: ModelType


class LLM(ABC):
    def __init__(
        self,
        model: Model,
        apiKey: str,
        messages: Optional[List[Dict[str, str]]] = None,  # Change this line
        temperature: float = 0.0,
        systemPrompt: Optional[str] = None,
        maxTokens: int = 2048,
        logFile: Optional[str] = None,
    ) -> None:
        messages = messages if messages is not None else []
        self.apiKey = apiKey
        self.messages = messages
        self.temperature = temperature
        self.systemPrompt = systemPrompt
        self.maxTokens = maxTokens
        self.model = model

        # logger setup
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)  # Set default log level
        
        # Create a JSON formatter
        json_formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s %(name)s %(funcName)s')
        
        # Check if logFile is None, in that case use console logging (pseudo-logging)
        if logFile is None:
            # Pseudo-logging with RichHandler (for console output)
            from rich.logging import RichHandler
            rich_handler = RichHandler()
            self.logger.addHandler(rich_handler)
        else:
            # If logFile is provided, log to a file in JSON format            
            LOG_FILE = logFile
            file_handler = logging.FileHandler(LOG_FILE)
            file_handler.setFormatter(json_formatter)
            self.logger.addHandler(file_handler)
            

        # Handle case where `model` is passed as a string
        if type(model) is str:
            self.logger.error("Model name must be a Model object. Fixed temporarily.")
            self.model = Model(model, ModelType.textandimage)
            model = self.model
        
        self.logger.info(
            {   
                "message": "Initializing LLM",
                "model": model.name,
                "modelType": model.typeof.value,
                "temperature": temperature
            }
        )

        # Set the appropriate message handler based on the model type
        self.addMessage = self.addMessageTextOnly if model.typeof == ModelType.textonly else self.addMessageVision
        
        if systemPrompt:
            self.addMessage(Role.system, systemPrompt)

        
    @abstractmethod
    def run(self, prompt: str, save: bool = True) -> str:
        raise NotImplementedError

    @abstractmethod
    def streamRun(self, prompt: str, save: bool = True) -> str:
        raise NotImplementedError
    
    @abstractmethod
    def constructClient(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def testClient(self) -> None:
        raise NotImplementedError

    
    def addMessage(self, role: Role, content: str, imageUrl: Optional[str] = None) -> None:
        ...
    
    
    def addMessageVision(self, role: Role, content: str, imageUrl: Optional[str] = None) -> None:
        
        if imageUrl is None:
            return self.addMessageTextOnly(role, content, imageUrl)
        if type(role) is str:
            role = Role[role]

        message: Dict[str, list] = {"role": role.value, "content": []}

        if content:
            message["content"].append(
                {
                    "type": "text",
                    "text": content
                }
            )

        if imageUrl:
            message["content"].append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": imageUrl
                    }
                }
            )

        self.messages.append(message)

    def addMessageTextOnly(self, role: Role, content: str, imageUrl: Optional[str] = None) -> None:
        if type(role) is str:
            role = Role[role]

        if imageUrl is not None:
            self.logger.error("Image URL is not supported for text-only model. Ignoring the image URL.")
            
        self.messages.append({
            "role": role.value,
            "content": content
        })

    
    def getMessage(self, role: Role, content: str, imageUrl: Optional[str] = None) -> List[Dict[str, str]]:        
        if type(role) is str:
            role = Role[role]

        if imageUrl is not None:
            message: Dict[str, list] = {"role": role.value, "content": []}

            if content:
                message["content"].append(
                    {
                        "type": "text",
                        "text": content
                    }
                )

            if imageUrl:
                message["content"].append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": imageUrl
                        }
                    }
                )
            return message
        else:
            return {
                "role": role.value,
                "content": content
            }
        
    
    def log(self, **kwargs) -> None:
        self.logger.info(kwargs)


if __name__ == "__main__":
    print(Role.system.value)

import google.generativeai as genai
from google.generativeai.types import File
from google.generativeai import GenerationConfig, list_models

from typing import Optional, List, Dict
from dotenv import load_dotenv
from rich import print
import base64
import requests
import PIL.Image
from io import BytesIO
from enum import Enum

class ModelType(Enum):
    textonly = "textonly"
    textandimage = "textandimage"
    textandfile = "textandfile"

load_dotenv()

GEMINI_1_5_FLASH_002 = Model(name="gemini-1.5-flash-002", typeof=ModelType.textandfile)
GEMINI_1_5_FLASH_8B_EXP_0924 = Model(name="gemini-1.5-flash-8b-exp-0924", typeof=ModelType.textandfile)
GEMINI_1_5_FLASH_8B_LATEST = Model(name="gemini-1.5-flash-8b-latest", typeof=ModelType.textandfile)
GEMINI_1_5_FLASH_8B_001 = Model(name="gemini-1.5-flash-8b-001", typeof=ModelType.textandfile)
GEMINI_1_5_FLASH_8B = Model(name="gemini-1.5-flash-8b", typeof=ModelType.textandfile)
GEMINI_1_5_FLASH_8B_EXP_0827 = Model(name="gemini-1.5-flash-8b-exp-0827", typeof=ModelType.textandfile)
GEMINI_1_5_FLASH_001 = Model(name="gemini-1.5-flash-001", typeof=ModelType.textandfile)
GEMINI_1_5_FLASH = Model(name="gemini-1.5-flash", typeof=ModelType.textandfile)


GEMINI_1_0_PRO_LATEST = Model(name="gemini-1.0-pro-latest", typeof=ModelType.textandimage)
GEMINI_1_0_PRO = Model(name="gemini-1.0-pro", typeof=ModelType.textandimage)
GEMINI_PRO = Model(name="gemini-pro", typeof=ModelType.textandimage)
GEMINI_1_0_PRO_001 = Model(name="gemini-1.0-pro-001", typeof=ModelType.textandimage)
GEMINI_1_0_PRO_VISION_LATEST = Model(name="gemini-1.0-pro-vision-latest", typeof=ModelType.textandimage)
GEMINI_PRO_VISION = Model(name="gemini-pro-vision", typeof=ModelType.textandimage)
GEMINI_1_5_PRO_LATEST = Model(name="gemini-1.5-pro-latest", typeof=ModelType.textandimage)
GEMINI_1_5_PRO_001 = Model(name="gemini-1.5-pro-001", typeof=ModelType.textandimage)
GEMINI_1_5_PRO_002 = Model(name="gemini-1.5-pro-002", typeof=ModelType.textandimage)
GEMINI_1_5_PRO = Model(name="gemini-1.5-pro", typeof=ModelType.textandimage)


def getImageByUrl(url: str) -> PIL.Image.Image:
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad status codes
        return PIL.Image.open(BytesIO(response.content))
    except Exception as e:
        raise ValueError(f"Failed to load image from URL: {str(e)}")


def getImageByBase64(imageBase64: str) -> PIL.Image.Image:
    if imageBase64.startswith("data:image/"):
        imageBase64 = imageBase64.split(",")[1]
    return PIL.Image.open(BytesIO(base64.b64decode(imageBase64)))


def getImageByFile(file: str) -> PIL.Image.Image:
    return PIL.Image.open(file)

def getImage(any: str | PIL.Image.Image | bytes) -> PIL.Image.Image:
    def checkIfUrl(any: str) -> bool:
        return any.startswith("http")
    if checkIfUrl(any):
        return getImageByUrl(any)
    elif isinstance(any, str):
        return getImageByBase64(any)
    elif isinstance(any, bytes):
        return getImageByFile(any)
    else:
        raise ValueError("Invalid image type")

def convert_openai_to_gemini(openai_messages: list) -> list:
    """
    Convert OpenAI message format to Gemini message format.
    
    Args:
        openai_messages (list): Messages in OpenAI format
        
    Returns:
        list: Messages in Gemini format with balanced user/model interactions
    """

    # Initial conversion to Gemini format
    gemini_messages = []
    system_messages = []

    # Convert messages to Gemini format
    for message in openai_messages:
        role = message["role"]
        content = message["content"]

        if role == "system":
            system_messages.append(content)
        elif role == "user":
            if isinstance(content, list):
                for content_item in content:
                    if content_item["type"] == "text":
                        gemini_messages.append({
                            "role": "user",
                            "parts": [content_item["text"]]
                        })
                    elif content_item["type"] == "image_url":
                        gemini_messages.append({
                            "role": "user",
                            "parts": [getImage(content_item["image_url"]["url"])]
                        })
            else:
                gemini_messages.append({
                    "role": "user",
                    "parts": [content]
                })
        elif role == "assistant":
            gemini_messages.append({
                "role": "model",
                "parts": [content]
            })

    # Combine consecutive messages from the same role
    consolidated_messages = []
    previous_role = None

    for message in gemini_messages:
        current_role = message["role"]
        if current_role == previous_role:
            consolidated_messages[-1]["parts"].append(message["parts"][0])
        else:
            consolidated_messages.append(message)
            previous_role = current_role

    # Balance user/model interactions by inserting empty messages
    balanced_messages = []
    previous_role = None

    for message in consolidated_messages:
        current_role = message["role"]
        if current_role == previous_role == "user":
            balanced_messages.append({
                "role": "model",
                "parts": ["\n"]
            })
            previous_role = "model"
        elif current_role == previous_role == "model":
            balanced_messages.append({
                "role": "user",
                "parts": ["\n"]
            })
            previous_role = "user"
        
        balanced_messages.append(message)
        previous_role = current_role

    return balanced_messages


class Gemini(LLM):
    def __init__(
        self,
        model: Model,
        apiKey: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        temperature: float = 1.0,
        systemPrompt: Optional[str] = None,
        maxTokens: int = 2048,
        cheatCode: Optional[str] = None,
        logFile: Optional[str] = None,
        extra: Dict[str, str] = {}
    ):
        messages = messages if messages is not None else []
        super().__init__(model, apiKey, messages, temperature, systemPrompt, maxTokens, logFile)
        
        self.extra = extra
        self.cheatCode = cheatCode
        self.files: List[File] = []
        
        # Create the model
        self.generation_config = GenerationConfig(
            temperature=temperature,
            top_p=0.95,
            top_k=40,
            max_output_tokens=maxTokens,
            response_mime_type="text/plain",
        )
        self.client: genai.GenerativeModel = self.constructClient()
        genai.configure(api_key=apiKey if apiKey is not None else os.environ["GEMINI_API_KEY"])
        
        if cheatCode is None:
            p = self.testClient()
            if p:
                self.logger.info("Test successful for Gemini API key. Model found.")
        else:
            self.logger.info("Cheat code provided. Model found.")

    def constructClient(self):
        try:
            return genai.GenerativeModel(
                model_name=self.model.name,
                generation_config=self.generation_config,
                system_instruction=self.systemPrompt,
            )
        except Exception as e:
            print(e)
            self.logger.error(e)

    def testClient(self):
        try:
            models: List[str] = [i.name.removeprefix("models/") for i in list_models()]
            if self.model.name not in models:
                raise Exception(f"Model {self.model.name} not found!")
            return True
        except Exception as e:
            print(e)
            self.logger.error(e)
    
    def run(self, prompt: str = "", imageUrl: Optional[str] = None, files: Optional[List[File]] = None, save: bool = True) -> str:
        toSend = []
        if save and prompt:
            self.addMessage(Role.user, prompt, imageUrl)
        elif not save and prompt:
            toSend.append(self.getMessage(Role.user, prompt, imageUrl))
        try:
            
            history = convert_openai_to_gemini(self.messages + toSend)
            if files is not None:
                if history[-1]["role"] == "user":
                    history[-1]["parts"] = files + history[-1]["parts"]
                else:
                    history.append({
                        "role": "user",
                        "parts": files
                    })
            
            chat = self.client.start_chat(
                history=history
            )       
            response = chat.send_message("\n", **self.extra)
        except Exception as e:
            print(e)
            self.logger.error(e)
            return "Please check log file some error occured."
        self.logger.info(response)
        
        if save:
            self.addMessage(Role.assistant, response.text)
        return response.text

    def streamRun(self, prompt: str = "", imageUrl: Optional[str] = None, save: bool = True):
        toSend = []
        if save and prompt:
            self.addMessage(Role.user, prompt, imageUrl)
        elif not save and prompt:
            toSend.append(self.getMessage(Role.user, prompt, imageUrl))
        try:
            chat = self.client.start_chat(
                history=convert_openai_to_gemini(self.messages + toSend)
            )
            response = chat.send_message("\n", stream=True, **self.extra)
        except Exception as e:
            print(e)
            self.logger.error(e)
            return "Please check log file some error occured."
        try:
            final_response = ""
            for chunk in response:
                final_response += chunk.text
                yield chunk.text
            if save:
                self.addMessage(Role.assistant, final_response)
            return final_response
        except Exception as e:
            print(e)
            self.logger.error(e)
            return "Please check log file some error occured."


import time


def upload_to_gemini(path, mime_type=None):
  """Uploads the given file to Gemini.

  See https://ai.google.dev/gemini-api/docs/prompting_with_media
  """
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

def wait_for_files_active(files):
  """Waits for the given files to be active.

  Some files uploaded to the Gemini API need to be processed before they can be
  used as prompt inputs. The status can be seen by querying the file's "state"
  field.

  This implementation uses a simple blocking polling loop. Production code
  should probably employ a more sophisticated approach.
  """
  print("Waiting for file processing...")
  for name in (file.name for file in files):
    file = genai.get_file(name)
    while file.state.name == "PROCESSING":
      print(".", end="", flush=True)
      time.sleep(3)
      file = genai.get_file(name)
    if file.state.name != "ACTIVE":
      raise Exception(f"File {file.name} failed to process")
  print("...all files ready")
  print()


if __name__ == "__main__":
    files = [
    upload_to_gemini(r"static\video\video.mp4"),
    ]
    # Some files have a processing delay. Wait for them to be ready.
    wait_for_files_active(files)
    llm = Gemini(GEMINI_1_5_FLASH, apiKey="AIzaSyBA1BtwwX7PLNqIkDiZeVnsKt1Sa-_jp_c")

    print(files)
    print(llm.run("what is in the file?", files=files))