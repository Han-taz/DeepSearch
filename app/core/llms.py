from langchain_openai import ChatOpenAI
from app.core.config import settings

class LLMManager:
    _instances = {}
    
    @classmethod
    def get_llm(cls, model: str, temperature: float = 0.0):
        key = f"{model}_{temperature}"
        if key not in cls._instances:
            cls._instances[key] = create_llm(model=model, temperature=temperature)
        return cls._instances[key]
    
def create_llm(model:str="gpt-4o-mini", temperature:float=0.0):
    if model == "gpt-4o":
        return ChatOpenAI(model=model,
                        openai_api_key=settings.llm.openai_api_key,
                        temperature=temperature,
                        timeout=20,
                        max_retries=3,
                        streaming=True)
    elif model == "gpt-4o-mini":
        return ChatOpenAI(model=model,
                        openai_api_key=settings.llm.openai_api_key,
                        temperature=temperature,
                        timeout=20,
                        max_retries=3,
                        streaming=True)

    try:
        return ChatOpenAI(model=model,
                    openai_api_key=settings.llm.openai_api_key,
                    temperature=temperature,
                    timeout=20,
                    max_retries=3,
                    streaming=True)
    except:
        raise ValueError(f"Invalid model name: {model}")



class LLMManager:
    _instances = {}
    
    @classmethod
    def get_llm(cls, model: str, temperature: float = 0.0):
        key = f"{model}_{temperature}"
        if key not in cls._instances:
            cls._instances[key] = create_llm(model=model, temperature=temperature)
        return cls._instances[key]