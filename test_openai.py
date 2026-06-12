cdimport os
from langchain_openai import ChatOpenAI

# 1. Check if the terminal successfully passed the environment variable
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ ERROR: Your OPENAI_API_KEY environment variable is not set!")
    print("Please run: set OPENAI_API_KEY=your_key (Windows) or export OPENAI_API_KEY=your_key (Mac)")
else:
    print("🔎 Environment variable detected. Testing connection to OpenAI server...")
    try:
        # 2. Attempt a fast, low-cost token execution check
        llm = ChatOpenAI(model="gpt-4o", max_tokens=10)
        response = llm.invoke("Say the word SUCCESS and nothing else.")
        
        # 3. Output results
        print("\n✅ CONNECTION SUCCESSFUL!")
        print(f"OpenAI Response: {response.content.strip()}")
        
    except Exception as e:
        print("\n❌ CONNECTION FAILED!")
        print(f"Error Details: {str(e)}")
