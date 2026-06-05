import os
import litellm
from litellm import completion as original_completion

def patched_completion(*args, **kwargs):
    messages = kwargs.get("messages", [])
    for msg in messages:
        if isinstance(msg, dict):
            msg.pop("cache_breakpoint", None)
            if "content" in msg and isinstance(msg["content"], list):
                for block in msg["content"]:
                    if isinstance(block, dict):
                        block.pop("cache_breakpoint", None)
    return original_completion(*args, **kwargs)

litellm.completion = patched_completion

TAVILY_API_KEY = "your api key"
GROQ_API_KEY = "your-groq-api-key-here"

os.environ["GROQ_API_KEY"] = GROQ_API_KEY
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
os.environ["LITELLM_CACHE"] = "False"