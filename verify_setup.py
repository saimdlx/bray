import os
import sys

# Mock API keys for verification if not present
if not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = "mock_key"
if not os.getenv("YELP_API_KEY"):
    os.environ["YELP_API_KEY"] = "mock_key"
if not os.getenv("DISCORD_TOKEN"):
    os.environ["DISCORD_TOKEN"] = "mock_token"

# Set User Agent to avoid warnings/errors
os.environ["USER_AGENT"] = "BrayBot/1.0"

try:
    print("Importing modules...")
    import discord
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langgraph.graph import StateGraph
    from playwright.sync_api import sync_playwright
    import agent.core
    import agent.tools
    import bot
    print("Imports successful.")

    print("Initializing Agent...")
    a = agent.core.Agent()
    print("Agent initialized.")
    
    print("Verifying Tools...")
    tools = agent.tools.get_tools()
    print(f"Tools loaded: {[t.name for t in tools]}")
    
    # Test web_search tool directly (mocking network if needed, but let's try real if possible or just check existence)
    # We won't call it to avoid network issues in this environment if blocked, but imports are key.
    
    print("Setup verification passed!")
    
except Exception as e:
    print(f"Verification failed: {e}")
    sys.exit(1)
