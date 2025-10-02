from openai import OpenAI
from dotenv import load_dotenv
import os
from main import get_weather
from pydantic import BaseModel, Field
from typing import Optional

client= OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

SYSTEM_PROMPT = """
You are an AI agent that can use tools to help the user. You have access to the following tool:
TOOL: get_weather()

You have to strictly follow these rules:
-Always respond in json format 
-If you need to use a tool, use tool
-always give response in format that it can load in json.loads
-During creating final response explain the user that the weather is good adn tell about pros and cons of that weather.

There will be four phases in your response:
- START: When you start the conversation, greet the user and ask how you can help them.
- PLAN: When you need to plan your next steps, describe what you plan to do next
- TOOL: When you need to use a tool, specify the tool name and the input parameters
- ANSWER: When you have the final answer for the user, provide the answer


Strictly follow this format :
{"steps":"START" | "PLAN" | "TOOL"  | "ANSWER","content":"string"}


EXAMPLE RESPONSES:
{"steps":"START,"content":"Hello! How can I assist you today?"}
{"steps":"PLAN","content":"I need to get the current weather in New York City"}
{"steps":"PLAN","content":"I need to get the weather forcast by using get_weather() tool"}
{"steps":"TOOL","tool":"get_weather()","tool_input":"New Delhi"
{"steps":"TOOL","tool":"get_weather()","tool_output":{"temperature":75,"condition":"clear"}}
{"steps":"ANSWER","content":"The current weather in New York is 75°F with clear skies. This weather is suitable for humans to go outside and enjoy outdoor activities."}
query ends here.

EXAMPLE 2 RESPONSE:
{"steps":"START","content":"Hello! How can I assist you today?"}
{"steps":"PLAN","content":"I need to get the weather forcast by using get_weather() tool"}
{"steps":"TOOL","tool":"get_weather()","tool_input":{"location":"San Francisco"}}
{"steps":"TOOL","tool":"get_weather()","tool_output":{"temperature":60,"condition":"foggy"}}
{"steps":"ANSWER","content":"The current weather in San Francisco is 60°F with foggy skies. This weather is suitable for humans to go outside but they should carry a light jacket."}

"""

USER_PROMPT = input("Enter your query about weather: ")

message_history = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": USER_PROMPT}
]

class Structured_response(BaseModel):
    step:str = Field(...,description="This is ID of the steps")
    content:Optional[str]  = Field(...,description="This is the content area")
    tool:Optional[str] = Field(...,description="This si used to tell weather which tool is being used. ")
    input:Optional[str] = Field(...,description="This is input field")

while True:
    try:
        response = client.chat.completions.parse(
            model="gemini-2.0-flash",
            response_format=Structured_response,
            messages=message_history
        )
        raw_results = response.choices[0].message.content
        parsed_results = response.choices[0].message.parsed
        print(f"Raw response: {parsed_results}")
        if not parsed_results:
            print("No response from the model.")
       
        
        
        
        message_history.append({"role":"assistant","content":raw_results})

        try:
        
            if parsed_results.step == "START":
                print("AGENT: ", parsed_results.content)
                continue
            
            if parsed_results.step == "PLAN":
                print("AGENT PLANNING:" , parsed_results.content)
                continue
            if parsed_results.step == "TOOL":
                tool_name = parsed_results.tool
                tool_input = parsed_results.input
                if tool_name == "get_weather()":
                    
                    tool_output = get_weather(tool_input)
                    print(f"TOOL OUTPUT: {tool_output}")
                    message_history.append({"role":"user","content":f'{{"steps":"TOOL","tool":"get_weather()","tool_output":{tool_output}}}'})
                    continue
            if parsed_results.step == "ANSWER":
                print("FINAL ANSWER: ", parsed_results.content)
                break
        except Exception as e:
            print(f"Error processing START or PLAN or TOOL step: {e}")    




    except Exception as e:
        print(f"Error during API call: {e}")   