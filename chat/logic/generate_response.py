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
            "description":f"email of user, e.g example@gmail.com"
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

    messages.append(
        {"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous. Ensure to validate user inputs for names and email addresses before proceeding. Specifically, names should be validated to ensure they are conventional human names and not other nouns or phrases. If the input is ambiguous or does not meet the criteria, prompt the user for clarification. Validate the sender's name to ensure it is a normal  name. If the name is not a normal name (e.g., a fruit, vegetable, animal, object or non-name term), request changing to normal human name from the user, until he provides it.Confirm that the recipient's email address is in a valid email format, not exaple@ or fake@. If not, ask the user to provide a valid email address. Tell about fields just like name, email, and message, tell about restrictions only if inacceptable data for the fields provided"}
    )

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
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            stream=True
        )

        tool_calls = None

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
                model="gpt-3.5-turbo-1106",
                messages=messages,
                stream=True
            )

            for chunk in follow_up_response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    except Exception as e:
        print(f"Error generating response: {e}")
        yield f"I'm sorry, I couldn't process your request right now. the error {e}"