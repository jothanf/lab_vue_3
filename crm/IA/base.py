import os
from openai import OpenAI

class BaseAIService:
    def __init__(self):
        self.client = None
    
    def initialize_client(self):
        raise NotImplementedError

class OpenAIService(BaseAIService):
    def __init__(self):
        super().__init__()
        self.initialize_client()
    
    def initialize_client(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class WhisperService(BaseAIService):
    # Para transcripción de voz
    pass

class DalleService(BaseAIService):
    # Para generación de imágenes
    pass 