import os
import requests
import json
from flask import Flask, request

app = Flask(__name__)

ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')

@app.route('/webhook', methods=['GET', 'POST'])
def webhook_handler():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge'), 200
        else:
            return 'Error de verificación', 403

    if request.method == 'POST':
        data = request.get_json()
        print(f"Recibido: {json.dumps(data, indent=2)}")

        try:
            if data['entry'][0]['changes'][0]['value']['messages'][0]['type'] == 'text':
                numero_cliente = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
                cuerpo_mensaje = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
                
                print(f"Mensaje de {numero_cliente}: '{cuerpo_mensaje}'")

                if 'hola' in cuerpo_mensaje.lower():
                    send_whatsapp_message(numero_cliente, 'hello_world')

        except (KeyError, IndexError, TypeError):
            pass

        return 'OK', 200

def send_whatsapp_message(to_number, template_name):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": { "name": template_name, "language": { "code": "en_US" } }
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"Respuesta de la API de envío: {response.status_code} - {response.text}")
