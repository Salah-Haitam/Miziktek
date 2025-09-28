from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import ChatMessage
import json
import os
from dotenv import load_dotenv
import openai

# Configuration OpenAI
import pathlib
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / 'api.env')
openai.api_key = os.getenv('OPENAI_API_KEY')

# Vérifier si la clé API est correcte
if not openai.api_key:
    raise ValueError("La clé API OpenAI n'est pas définie")

# Test de la connexion à OpenAI
def test_openai_connection():
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un assistant musical intelligent."},
                {"role": "user", "content": "Test de connexion"}
            ],
            max_tokens=1
        )
        return True
    except Exception as e:
        print(f"Erreur lors de la connexion à OpenAI: {str(e)}")
        return False

# Fonction pour obtenir une réponse du chatbot
def get_bot_response(message):
    try:
        # Vérifier la connexion à OpenAI
        if not test_openai_connection():
            return "Désolé, je ne peux pas me connecter à OpenAI. Veuillez vérifier votre clé API."
        
        # Configuration des messages pour le contexte
        messages = [
            {"role": "system", "content": "Tu es un assistant musical intelligent. Tu peux aider les utilisateurs à trouver de la musique, des artistes et répondre à leurs questions sur la musique."},
            {"role": "user", "content": message}
        ]

        # Appel à l'API OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )

        # Récupérer la réponse
        bot_response = response.choices[0].message.content.strip()
        return bot_response

    except Exception as e:
        print(f"Erreur lors de la génération de la réponse: {str(e)}")
        return f"Désolé, une erreur est survenue. Veuillez réessayer plus tard. Erreur: {str(e)}"

@login_required
def chatbot_view(request):
    return render(request, 'chatbot/chat.html')

@csrf_exempt
@login_required
def get_response(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            if user_message:
                # Sauvegarder le message utilisateur
                user_msg = ChatMessage.objects.create(
                    user=request.user,
                    content=user_message,
                    is_user_message=True
                )
                
                # Obtenir la réponse du chatbot
                response = get_bot_response(user_message)
                
                # Sauvegarder la réponse
                user_msg.response = str(response)
                user_msg.save()
                
                return JsonResponse({'response': str(response)})
            
            return JsonResponse({'error': 'No message received'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
