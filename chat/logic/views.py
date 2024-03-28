from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Conversation
from .generate_response import generate_response, initial_role
import json
from django.shortcuts import get_object_or_404
from decouple import config



class ChatBotView(APIView):
    print('\n\n\n\n\n\n\nn\n\n\n\n\n\n\n\n\n\n')
    print('1')
    print('\n\n\n\n\n\n\nn\n\n\n\n\n\n\n\n\n\n')
    def post(self, request, *args, **kwargs):
        print('\n\n\n\n\n\n\nn\n\n\n\n\n\n\n\n\n\n')
        print('2')
        print('\n\n\n\n\n\n\nn\n\n\n\n\n\n\n\n\n\n')
        chat_id = request.data.get('chat_id')
        user_question_text = request.data.get('message')
        rest_key =  request.data.get('rest')
        key = config('MY_KEY')
        if rest_key == key:
            user_question = [

                    {"role": "user", "content": f'question "{user_question_text}"'}

                ]

            if chat_id is None:
                answer = generate_response(user_question=user_question_text)

                reply_history = [

                    {"role": "assistant", "content": initial_role},
                    {"role": "assistant", "content": answer},

                ]

                conversation = Conversation.objects.create(
                    user_input=json.dumps(user_question),
                    response=json.dumps(reply_history),
                )
                
                return Response(
                    {
                        "chat_id": str(conversation.chat_id),
                        "latest_response": answer
                    }
                )

            else:
                conversation = get_object_or_404(Conversation, chat_id=chat_id)

                prev_questions = json.loads(conversation.user_input)
                prev_responses = json.loads(conversation.response)
                
                conversation_history = prev_responses + prev_questions
                
                new_answer = generate_response(user_question_text, conversation_history)


                conversation.user_input = json.dumps(
                    prev_questions + 
                        [
                            {"role": "user", "content": user_question_text}
                        ]
                    )
                conversation.response = json.dumps(
                    prev_responses + 
                        [ 
                            {
                            "role": "assistant", "content": new_answer
                            }
                        ]
                    )
                conversation.save()
                
                return Response(
                    {
                        "latest_response": new_answer,
                    }
                )


        return Response({"error": "access denied"}, status=404)



