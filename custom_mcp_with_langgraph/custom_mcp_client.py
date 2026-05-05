import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
import os
from dotenv import load_dotenv
load_dotenv()

async def main():
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    
    # client = MultiServerMCPClient(
    #     {
    #         "math": {
    #             "command": "python",
    #             "args": ["E:/MCP/custom_mcp_with_langgraph/custom_mcp_server.py"],
    #             "transport": "stdio"
    #         }
    #     }
    # )
    
    client = MultiServerMCPClient(
        {
            "math": {
                "transport": "streamable-http",
                "url": "http://127.0.0.1:8000/mcp"
            }
        }
    )
    
    tools = await client.get_tools()
    llm_with_tools = llm.bind_tools(tools)
    
    tool_node = ToolNode(tools)
    
    async def call_model(state: MessagesState):
        messages = state['messages']
        response =await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}
    
    builder = StateGraph(MessagesState)
    
    builder.add_node("call_model", call_model)
    builder.add_node("tools", tool_node)
    
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges("call_model", tools_condition)
    builder.add_edge("tools", "call_model")
    builder.add_edge("call_model", END)
    
    graph = builder.compile()
    
    while True:
        user_input = input("\ninsert your query here: ")
        
        if user_input.strip().lower() in ["quit", "exit"]:
            print("GoodBye!!!")
            break
        result = await graph.ainvoke({"messages": user_input})
        print(result['messages'][-1].content)
    
    
if __name__ == "__main__":
    asyncio.run(main())
    