import edge_tts
import re
from happy.logging import Logger

l = Logger(__file__)


def remove_emojis(data: str) -> str:
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', data)


async def fetch_audio(text, AssistantVoice = "en-US-JennyNeural") -> bytes:
    text = remove_emojis(text)
    try:
        communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural", pitch='+5Hz', rate='+22%')
        audio_bytes = b""
        async for element in communicate.stream():
            if element["type"] == 'audio':
                audio_bytes += element["data"]
        return audio_bytes
    except Exception as e:
        l.error(e)
        return b""


async def TextToSpeechBytes(Text, AssistantVoice = "en-US-JennyNeural") -> bytes:
    Text = str(Text)
    return await fetch_audio(Text, AssistantVoice)

if __name__ == "__main__":
    while True:
        print(TextToSpeechBytes(input(">>> ")))
 
