from openai import OpenAI
from typing import Literal
from .bot_funcs import send_emails
import json
from decouple import config

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
            "description":f"email of user, e.g example@gmail.com and not {str(config('email'))}"
        }
    },
    "required": ["name", 'message', "email_of_customer"]
}


def generate_response(user_question, prev_question=None):
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

    messages = []

    if not prev_question:
        messages.append(
                {
                    "role": "assistant",
                    "content": initial_role,
                }
            )

    else:
        messages.extend(
            prev_question
            )

    messages.append(
            {"role": "user", "content": user_question}
            )
            
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools,
            tool_choice='auto',
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            available_functions = {
                "send_emails": send_emails,
            }

            messages.append(response_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                if function_name == "send_emails":
                    function_response = function_to_call(
                        name=function_args.get("name"),
                        message=function_args.get("message"),
                        email_of_customer=function_args.get("email_of_customer")
                    )

            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": f'the response:{function_response}',
                }
            )

            follow_up_response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
        )
            return follow_up_response.choices[0].message.content

        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating response: {e}")
        return f"I'm sorry, I couldn't process your request right now. the error {e}"