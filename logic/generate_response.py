from openai import OpenAI
from typing import Literal
from .bot_funcs import send_emails
import json
from decouple import config
import openai

initial_role = f"""
{config('initial_role')}
"""

key = str(config('GPT'))

client = OpenAI(api_key=key,)



add_func_properties = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "The name of user"
        },
        "message": {
            "type": "string",
            "description": "message of user"
        },
        "email_of_customer": {
            "type": "string",
            "description":f"email of user, e.g example@gmail.com"
        }
    },
    "required": ["name", 'message', "email_of_customer"]
}


tools = [
        {
            "type": "function",
            "function": {
                "name": "send_emails",
                "description": "send techinical email andreyabout new orders",
                "parameters": add_func_properties
            },
        },
    ]

start_sys_message = "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous. Ensure to validate user inputs for names and email addresses before proceeding. Specifically, names should be validated to ensure they are conventional human names and not other nouns or phrases. If the input is ambiguous or does not meet the criteria, prompt the user for clarification. Validate the sender's name to ensure it is a normal  name. If the name is not a normal name (e.g., a fruit, vegetable, animal, object or non-name term), request changing to normal human name from the user, until he provides it.Confirm that the recipient's email address is in a valid email format, not exaple@ or fake@. If not, ask the user to provide a valid email address. Tell about fields just like name, email, and message, tell about restrictions only if inacceptable data for the fields provided"

def generate_response(user_question, prev_question=None):

    messages = []

    messages.append(
        {"role": "system", "content": start_sys_message} )

    if not prev_question:
        messages.append(
            {
                "role": "assistant",
                "content": initial_role,
            }
        )
    else:
        messages.extend(prev_question)

    messages.append({"role": "user", "content": user_question})

    try:

        tool_call_details = {
            "name": None,
            "arguments": ""
        }

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            stream=True
        )

        response_message = 'response is'

        message_id = None

        for chunk in response:

            if chunk.choices[0].delta.content is not None:
                
                yield chunk

                response_message += chunk.choices[0].delta.content

            if chunk.choices[0].delta.tool_calls:

                for tool_call in chunk.choices[0].delta.tool_calls:

                    if message_id is None and tool_call.id:
                        message_id = tool_call.id

                    if tool_call.function.name is not None:

                        tool_call_details["name"] = tool_call.function.name

                tool_call_details["arguments"] += tool_call.function.arguments

        
        if tool_call_details["name"] is not None:
            
            available_functions = {
                "send_emails": send_emails,
            }

            response_messages = {
                    "content": response_message,
                    "role": "assistant",
                    "tool_calls": [{
                        "id": message_id,
                        "tool_call_id": message_id,
                        "function": {
                            "arguments": tool_call_details["arguments"],
                            "name": tool_call_details["name"]
                        },
                        "type": "function"
                    }]
                }
                
            messages.append(response_messages)

            function_name = tool_call_details["name"]
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call_details["arguments"])
            
            if function_name == "send_emails":
                function_response = function_to_call(
                    name=function_args.get("name"),
                    message=function_args.get("message"),
                    email_of_customer=function_args.get("email_of_customer")
                )

            messages.append(
                {
                    "role": "tool",
                    "name": function_name,
                    'tool_call_id': message_id,
                    "content": f'the response:{function_response}',
                }
            )


            follow_up_response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                stream=True
            )


            for chunk in follow_up_response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk

    except Exception as e:
        print(f"Error generating response: {e}")
        yield f"I'm sorry, I couldn't process your request right now. the error {e}"