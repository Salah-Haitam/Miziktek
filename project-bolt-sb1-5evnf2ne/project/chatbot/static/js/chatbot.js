// Fonction pour ouvrir/fermer le chatbot
function toggleChatbot() {
    const chatbotContainer = document.getElementById('chatbot-container');
    const chatbotButton = document.getElementById('chatbot-button');
    
    if (chatbotContainer.style.display === 'none' || chatbotContainer.style.display === '') {
        chatbotContainer.style.display = 'block';
        chatbotButton.style.display = 'none';
    } else {
        chatbotContainer.style.display = 'none';
        chatbotButton.style.display = 'block';
    }
}

function addMessage(message, isUser = true) {
    const messagesContainer = document.getElementById('chat-messages');
    if (!messagesContainer) {
        console.error('Impossible de trouver le conteneur des messages');
        return;
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    messageDiv.textContent = message;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function sendMessage() {
    const input = document.getElementById('chat-input');
    const sendButton = document.getElementById('chat-send');
    
    if (!input || !sendButton) {
        console.error('Éléments du formulaire non trouvés');
        return;
    }
    
    const message = input.value.trim();
    if (!message) return;
    
    // Désactiver les éléments pendant l'envoi
    input.disabled = true;
    sendButton.disabled = true;
    
    // Ajouter le message de l'utilisateur
    addMessage(message, true);
    
    // Effacer l'input
    input.value = '';
    
    // Envoyer le message au serveur
    fetch('/chatbot/get-response/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        if (data.response) {
            addMessage(data.response, false);
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        addMessage('Désolé, une erreur est survenue. Veuillez réessayer plus tard.', false);
    })
    .finally(() => {
        // Réactiver les éléments
        input.disabled = false;
        sendButton.disabled = false;
    });
}

// Fonction pour récupérer le CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Écouter l'événement de pression de la touche Entrée
// Initialiser le chatbot
window.addEventListener('load', function() {
    const container = document.getElementById('chatbot-container');
    const input = document.getElementById('chat-input');
    const sendButton = document.getElementById('chat-send');
    
    if (!container || !input || !sendButton) {
        console.error('Éléments du chatbot non trouvés');
        return;
    }
    
    // Ajouter un message de bienvenue
    addMessage("Bonjour ! Je suis votre assistant musical. Comment puis-je vous aider aujourd'hui ?", false);
    
    // Configurer l'écouteur d'événements pour l'input
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Configurer l'écouteur d'événements pour le bouton d'envoi
    sendButton.addEventListener('click', sendMessage);
});

// Initialiser le chatbot
if (document.getElementById('chatbot-container')) {
    // Ajouter un message de bienvenue
    addMessage("Bonjour ! Je suis votre assistant musical. Comment puis-je vous aider aujourd'hui ?", false);
}
