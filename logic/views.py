from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Conversation
from .generate_response import generate_response, initial_role
import json
from decouple import config
from django.http import StreamingHttpResponse

class ChatBotView(APIView):
    def post(self, request, *args, **kwargs):
        chat_id = request.data.get('chat_id')
        user_question_text = request.data.get('message')
        rest_key = request.data.get('rest')
        key = config('MY_KEY')

        if rest_key != key:
            return Response({"error": "Access denied"}, status=404)

        user_question = [{"role": "user", "content": f'question "{user_question_text}"'}]

        if chat_id is None:
            response_chunks = generate_response(user_question=user_question_text)

            def chunk_generator(response_chunks):
                chunks = ''
                conversation = Conversation.objects.create()
                chat_id_to_send = str(conversation.chat_id)

                yield json.dumps({'chat_id': chat_id_to_send}) + '\n'

                for chunk in response_chunks:
                    chunks += chunk.choices[0].delta.content
                    message = str(chunk.choices[0].delta.content)
                    yield json.dumps({'message': message, 'id': chunk.id}) + '\n'

                reply = [
                    {"role": "assistant", "content": initial_role},
                    {"role": "assistant", "content": chunks},
                ]

                conversation.user_input = json.dumps(user_question)
                conversation.response = json.dumps(reply)
                conversation.save()

            return StreamingHttpResponse(chunk_generator(response_chunks), content_type='application/json')

        else:
            conversation = get_object_or_404(Conversation, chat_id=chat_id)
            prev_questions = json.loads(conversation.user_input)
            prev_responses = json.loads(conversation.response)

            conversation_history = prev_questions + prev_responses

            response_chunks = generate_response(
                user_question=user_question_text,
                prev_question=conversation_history
            )

            def chunk_generator1(response_chunks):
                chunks = ''
                for chunk in response_chunks:
                    chunks += chunk.choices[0].delta.content
                    message = str(chunk.choices[0].delta.content)
                    yield json.dumps({'message': message, 'id': chunk.id}) + '\n'

                reply = [{"role": "assistant", "content": chunks}]
                conversation.user_input = json.dumps(prev_questions + user_question)
                conversation.response = json.dumps(prev_responses + reply)
                conversation.save()

            return StreamingHttpResponse(chunk_generator1(response_chunks), content_type='application/json')
