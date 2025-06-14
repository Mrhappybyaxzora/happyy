import dotenv
import dotenv.variables
from happy.logging import Logger
from os import getenv, environ

ENVPATH = "env"
fun = dotenv.get_key if ENVPATH else getenv

logger = Logger(__file__)

Keys = {
    "Groq": None,
    "Cohere": None,
    "OpenAI": None,
    "HuggingFace": None,
    "Tunestudio": None,
    "MongoUri": None,
    "PLAY_HT_USER_ID": None,
    "PLAY_HT_API_KEY": None,
    "GEMINI_API_KEY": None,
    "ELEVENLABS_API_KEY": None
}

for key, value in Keys.items():
    envvar = fun(ENVPATH, key)
    if envvar is None:
        logger.internal_error(
            "Please set the " + key + " environment variable",
            "Environment variable " + key + " not found"
        )
    else:
        Keys[key] = envvar
        environ[key] = envvar
    

