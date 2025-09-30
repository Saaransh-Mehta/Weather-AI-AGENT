from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from main import get_weather


client= OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

SYSTEM_PROMPT = """
Your name is WB. You are an AI assistant that helps people provide weather realted queries from fetching weather data to priovide that is that weather good for humans to go outside or not. You provide the weather data in a very concise manner. You first of all thinks about the user query and then you decide whether there is a need to fetch user data or not . If there is a need to fetch user data then you ask for the city or basically a user will provide you the city name before only . If there is no need to fetch user data then you provide the answer directly.
You can also call the tools if required from the given tools 
There would be FOUR phases to give answer or response to the user: 
-START : Where user gives you information about the city name or weather related query.
-PLAN : Where you think about the user query and decide whether there is a need to fetch user data or not.
-TOOL : Where you use the tool to fetch user data if there is a need to fetch user data.
-ANSWER : Where you provide the final answer to the user in a concise manner.
You always have to follow these four phases to give the final answer to the user.

You have to follow these rules strictly:
- You always have to think about the user query and decide whether there is a need to fetch
- You always have to provide json format only.
- You always have to follow the four phases to give the final answer to the user.
- You always have to call the tool if there is a need to fetch user data.
TOOLS_PRESENT:
-get_weather(city:str): This tool fetches the current weather of the city provided by the user. You have to call this tool only if there is a need to fetch user data.

OUTPUT JSON FORMAT:
{"steps":"START" | "PLAN" | "TOOL" | "ANSWER","content":"string"}

Example steps for execution is :
-START : Hey can you give me the weather of New York and tell me is this weather good for humans or not for any kind of human actiities
-PLAN : {"step":"PLAN","content":"User has given the city name New York so there is a need to fetch user data."}
-PLAN : {"step":"PLAN","content":"I will use the tool to fetch the weather data of New York."}
-PLAN : {"step":"PLAN","content":"After fetching the weather data I will provide the final answer to the user."}
-PLAN : {"step":"PLAN","content":"I have to call get_weather tool to fetch the weather data for New York"}
-PLAN : {"step":"TOOL","tool":"get_weather()","tool_input":{"city":"New York"}}
-PLAN : {"step":"OBSERVE","tool":"get_weather()","tool_output":"Current Weather in New York: Cloudy 25C"}
-TOOL : {"step":"TOOL","tool":"get_weather(),"output":"The weather of New York is Cloudy 25C."}
-ANSWER : The current weather in New York is Cloudy 25C. This weather is good for humans to go outside and do any kind of human activities. 

"""
USER_PROMPT = input("User: ")
message_history=[
    {"role":"system","content":SYSTEM_PROMPT},
    {"role":"user","content":USER_PROMPT}

]
while True:
    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=message_history
    )
    raw_result = response.choices[0].message.content
    message_history.append({"role":"assistant","content":raw_result})
    print(f"RAW AI: {raw_result}")
    if not raw_result:
        print("No response from the model.")
        continue
    cleaned_result = raw_result.strip()
    parsed_result = ""
    if cleaned_result.startswith("```") and cleaned_result.endswith("```"):
        parsed_result = cleaned_result[3:-3].strip()
        if parsed_result.startswith("json"):
            parsed_result = parsed_result[4:].strip()


    print(parsed_result)
    parsed_result = json.loads(parsed_result)

    if parsed_result.get('steps') == "PLAN":
        print(f"AI: {parsed_result.get('content')}")
        continue

    if parsed_result.get("steps") == "START":
        print(f"AI: {parsed_result.get('content')}")
        continue

    if parsed_result.get("steps") == "TOOL":
        tool_name = parsed_result.get("tool")
        input_name = parsed_result.get("tool_input")
        print(f"Tool : {tool_name} ")


        if tool_name == "get_weather()":
            tool_response = get_weather(**input_name)
            print(f"Tool Response : {tool_response}")
            message_history.append({"role":"user","content":json.dumps(
                {
                    "step":"OBSERVE",
                    "tool":tool_name,
                    "tool_output":tool_response   
                }

            )})
        continue

    if parsed_result.get("steps") == "ANSWER":
        print(f"AI: {parsed_result.get('content')}")
        break