# test_llm.py
import os
from langchain_openai import ChatOpenAI

print("OPENAI_API_BASE:", os.getenv("OPENAI_API_BASE"))
print("GROQ_API_KEY present:", bool(os.getenv("GROQ_API_KEY")))

try:
    llm = ChatOpenAI(
        model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
        api_key=os.getenv("GROQ_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE"),
        temperature=0.0,
    )
    print("LLM client created OK.")
except Exception as e:
    print("LLM creation failed:", type(e).__name__, str(e))
