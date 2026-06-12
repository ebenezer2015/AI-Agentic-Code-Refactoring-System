import os
from langchain_openai import ChatOpenAI

# Set up access credentials safely
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "your-api-key")

# Base structural inference engine
llm = ChatOpenAI(
    model="gpt-4o", 
    temperature=0.0, 
    max_tokens=4000
)
