from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Annotated
import operator
from config import GOOGLE_API_KEY
from agent.tools import get_tools

# Define the state
class AgentState(TypedDict):
    messages: Annotated[List[HumanMessage | AIMessage | SystemMessage], operator.add]

class Agent:
    def __init__(self):
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in .env")
        
        self.tools = get_tools()
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        self.graph = self._build_graph()
        
        # Simple in-memory checkpointer/memory for now (dictionary of thread_id -> state)
        # In a real app, use a persistent checkpointer
        self.memory = {} 

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        def call_model(state):
            messages = state['messages']
            response = self.llm_with_tools.invoke(messages)
            return {"messages": [response]}

        def call_tools(state):
            messages = state['messages']
            last_message = messages[-1]
            
            # This is a simplified tool execution node. 
            # In a full LangGraph setup with ToolNode, this is handled automatically.
            # But let's do it manually for clarity or use the prebuilt ToolNode if available.
            # For this implementation, let's use the prebuilt ToolNode pattern if possible,
            # or just manual execution. Manual is safer for custom control.
            
            tool_calls = last_message.tool_calls
            results = []
            for tool_call in tool_calls:
                tool = next((t for t in self.tools if t.name == tool_call['name']), None)
                if tool:
                    print(f"Calling tool: {tool.name} with args: {tool_call['args']}")
                    try:
                        res = tool.invoke(tool_call['args'])
                    except Exception as e:
                        res = f"Error calling tool: {e}"
                    
                    # Create a ToolMessage (LangChain core)
                    from langchain_core.messages import ToolMessage
                    results.append(ToolMessage(tool_call_id=tool_call['id'], content=str(res)))
            
            return {"messages": results}

        def should_continue(state):
            messages = state['messages']
            last_message = messages[-1]
            if last_message.tool_calls:
                return "tools"
            return END

        workflow.add_node("agent", call_model)
        workflow.add_node("tools", call_tools)

        workflow.set_entry_point("agent")
        workflow.add_conditional_edges("agent", should_continue)
        workflow.add_edge("tools", "agent")

        return workflow.compile()

    async def process_message(self, message: str, user_id: str):
        # Initialize state if new user
        if user_id not in self.memory:
            self.memory[user_id] = {"messages": [
                SystemMessage(content="You are a helpful Discord assistant. You can search Yelp and the web to help users.")
            ]}
        
        # Add user message
        self.memory[user_id]["messages"].append(HumanMessage(content=message))
        
        # Run graph
        # Note: LangGraph is usually sync or async. 
        # We'll use invoke (sync) for simplicity unless we need async tools.
        # But since we are in an async discord handler, we should ideally use ainvoke.
        
        final_state = await self.graph.ainvoke(self.memory[user_id])
        
        # Update memory with the result
        # The result 'final_state' contains all messages including the new ones.
        self.memory[user_id] = final_state
        
        # Get the final response
        last_message = final_state["messages"][-1]
        return last_message.content
