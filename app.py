    # Importamos las herramientas necesarias
    import os
    import requests
    import json
    from flask import Flask, request

    # Creamos la aplicación web con Flask
    app = Flask(__name__)

    # Obtenemos las variables secretas que configuraremos en Render
    # Es más seguro que tenerlas escritas directamente en el código
    TOKEN_DE_ACCESO = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    TOKEN_DE_VERIFICACION = os.environ.get('VERIFY_TOKEN')
    ID_DE_NUMERO = os.environ.get('PHONE_NUMBER_ID')

    @app.route('/webhook', methods=['GET', 'POST'])
    def webhook():
        # --- VERIFICACIÓN DEL WEBHOOK (SOLO OCURRE UNA VEZ) ---
        if request.method == 'GET':
            # Meta envía este 'challenge' para verificar que la URL es tuya
            challenge = request.args.get('hub.challenge')
            verify_token_received = request.args.get('hub.verify_token')

            # Comparamos nuestro token de verificación con el que envió Meta
            if verify_token_received == TOKEN_DE_VERIFICACION:
                print(f"Webhook verificado correctamente. Challenge: {challenge}")
                return challenge, 200
            else:
                print(f"Error de verificación. Tokens no coinciden. Recibido: {verify_token_received}")
                return 'Error de verificación', 403

        # --- RECEPCIÓN DE MENSAJES (OCURRE CADA VEZ QUE ALGUIEN ESCRIBE) ---
        elif request.method == 'POST':
            data = request.get_json()
            print("Datos recibidos del webhook:", json.dumps(data, indent=2))

            # Extraemos la información relevante del mensaje
            try:
                # Nos aseguramos de que sea una notificación de mensaje de WhatsApp
                if 'entry' in data and data['entry'][0]['changes'][0]['value']['messaging_product'] == 'whatsapp':

                    # Información del mensaje
                    mensaje = data['entry'][0]['changes'][0]['value']['messages'][0]
                    numero_cliente = mensaje['from']
                    cuerpo_del_mensaje = mensaje['text']['body']

                    print(f"Mensaje de '{numero_cliente}': '{cuerpo_del_mensaje}'")

                    # --- AQUÍ VA TU LÓGICA DE RESPUESTA ---
                    # Ejemplo: si el cliente dice "hola", le respondemos con la plantilla "hello_world"
                    if "hola" in cuerpo_del_mensaje.lower():
                        enviar_mensaje(numero_cliente, "hello_world")

                    return 'Mensaje recibido', 200

            except (KeyError, IndexError) as e:
                # Esto ocurre si la notificación no es un mensaje (ej: una entrega, una lectura, etc.)
                print(f"Notificación no procesada (no es un mensaje de texto): {e}")
                pass # Ignoramos estas notificaciones para no generar un error

            return 'Evento recibido', 200

# Función para enviar mensajes usando la API (¡es nuestro código anterior!)
def enviar_mensaje(destino, plantilla):
    url = f"https://graph.facebook.com/v19.0/{ID_DE_NUMERO}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN_DE_ACCESO}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": destino,
        "type": "template",
        "template": {
            "name": plantilla,
            "language": {
                "code": "en_US"
            }
        }
    }

    print(f"Enviando plantilla '{plantilla}' a '{destino}'...")
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print("Mensaje enviado con éxito.")
    else:
        print(f"Error al enviar mensaje: {response.status_code}", response.text)

# Esto es necesario para que el servidor de Render inicie la aplicación
if __name__ == '__main__':
    # Render se encarga de definir el puerto, así que no nos preocupamos por eso
    app.run(debug=True, port=os.getenv('PORT', default=5000))
