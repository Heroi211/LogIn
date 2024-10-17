from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# Configurações do Twilio
account_sid = 'your_account_sid'
auth_token = 'your_auth_token'
client = Client(account_sid, auth_token)

def validate_phone_number(phone_number):
    try:
        phone_number_info = client.lookups.v1.phone_numbers(phone_number).fetch(type="carrier")
        return phone_number_info
    except TwilioRestException as e:
        print(f"Erro ao validar o número de telefone: {e}")
        return None

def send_whatsapp_message(to, body):
    message = client.messages.create(
        body=body,
        from_='whatsapp:+14155238886',  # Número do sandbox do Twilio
        to=f'whatsapp:{to}'
    )
    return message.sid

# Exemplo de uso
send_whatsapp_message('+5511999999999', 'Olá, este é um teste de mensagem do WhatsApp!')