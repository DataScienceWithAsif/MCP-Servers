import asyncio
import os
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv
load_dotenv()

async def main():
    owm_key = os.getenv("OWM_API_KEY")
    
    client = MultiServerMCPClient(
        {
            "weather":{
                "transport": "stdio",
                "command":"E:/MCP/langgraph_mcp_demo/mcp-openweather/mcp-weather.exe",
                "args":[],
                "env": {"OWM_API_KEY":owm_key}
            },
            "calculator":{
                "transport": "stdio",
                "command": "python",
                "args": ["-m", "mcp_server_calculator"]
            }
        }
    )
    
    tools = await client.get_tools()
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    llm_with_tools = llm.bind_tools(tools)
    
    def call_model(state: MessagesState):
        response= llm_with_tools.invoke(state['messages'])
        return {"messages": response}
    
    builder = StateGraph(MessagesState)
    builder.add_node("call_model", call_model)
    builder.add_node("tools", ToolNode(tools=tools))
    
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges("call_model", tools_condition)
    builder.add_edge("tools", "call_model")
    builder.add_edge("call_model", END)
    
    graph = builder.compile()
    
    # result = await graph.ainvoke({"messages":"what is weather in Islamabad today"})
    # print(result['messages'][-1].content)
    
    while True:
        user_question = input("\nAsk me anything related weather and calculator: \n")
        if user_question.strip().lower() in ["exit", "quit"]:
            print("GoodBye!")
            break
        else:
            print("\n----- Agent is Thinking -----")
            result = await graph.ainvoke({"messages": user_question})
            print("\n========= Asnwer ==========\n")
            print(result['messages'][-1].content)
            
    

if __name__ == "__main__":
    asyncio.run(main())