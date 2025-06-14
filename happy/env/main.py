import dotenv
import dotenv.variables
from happy.logging import Logger
from os import getenv, environ, path

ENVPATH = "env"
logger = Logger(__file__)

# Try to load from .env file first, then fall back to environment variables
def get_env_value(key: str) -> str:
    # First try to get from .env file
    if path.exists(ENVPATH):
        value = dotenv.get_key(ENVPATH, key)
        if value:
            return value
    
    # Then try to get from environment variables
    value = getenv(key)
    if value:
        return value
    
    return None

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
    envvar = get_env_value(key)
    if envvar is None:
        logger.internal_error(
            f"Please set the {key} environment variable",
            f"Environment variable {key} not found"
        )
    else:
        Keys[key] = envvar
        environ[key] = envvar
        logger.info(f"Loaded environment variable: {key}")
    

