import telebot
import time
import os
import requests
import threading
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Configurações AlphaPay
ALPHAPAY_TOKEN = os.getenv('ALPHAPAY_TOKEN')
PRODUCT_HASH = os.getenv('PRODUCT_HASH')
OFFER_HASH = os.getenv('OFFER_HASH')
GROUP_LINK = os.getenv('GROUP_LINK')

user_steps = {}
user_data = {} # Armazena dados temporários (Nome, CPF, Email)
transaction_mapping = {} # Mapeia hash da transação para chat_id

# --- INTEGRAÇÃO ALPHAPAY ---
def create_alphapay_transaction(chat_id):
    payload = {
        "amount": 1990, # R$ 19,90 em centavos
        "offer_hash": OFFER_HASH,
        "payment_method": "pix",
        "customer": {
            "name": "Cliente Telegram",
            "email": "cliente@gmail.com",
            "phone_number": "11989283928",
            "document": "26208784620"
        },
        "cart": [{
            "product_hash": PRODUCT_HASH,
            "title": "Grupo VIP + Punhetinha Guiada",
            "price": 1990,
            "quantity": 1,
            "operation_type": 1,
            "tangible": False
        }],
        "transaction_origin": "api",
        "postback_url": os.getenv('POSTBACK_URL')
    }
    
    url = f"https://api.alphapaybrasil.com.br/v1/transactions?api_token={ALPHAPAY_TOKEN}"
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Erro AlphaPay: {e}")
        return None

# --- WEBHOOK SERVER (FLASK) ---
app = Flask(__name__)

@app.route('/webhook/alphapay', methods=['POST'])
def alphapay_webhook():
    content = request.json
    if content and content.get('status') == 'paid':
        tx_hash = content.get('transaction_hash')
        chat_id = transaction_mapping.get(tx_hash)
        
        if chat_id:
            bot.send_message(chat_id, "✅ Pagemento confirmado, meu amor! ❤️")
            time.sleep(2)
            bot.send_message(chat_id, f"Aqui está o link do seu acesso vitalício: {GROUP_LINK}")
            bot.send_message(chat_id, "Seja muito bem-vindo(a) ao meu mundinho VIP! 😈🔥")
            user_steps[chat_id] = 0
            
    return jsonify({"status": "ok"}), 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

# --- BOT LOGIC ---

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_steps[chat_id] = 1
    time.sleep(5)
    bot.send_chat_action(chat_id, 'typing')
    time.sleep(5)
    bot.send_message(chat_id, "oi gatinho")
    
    bot.send_chat_action(chat_id, 'typing')
    time.sleep(6)
    bot.send_message(chat_id, "Me chamo Alessandra, tenho 19 aninhos... prazer 😉")
    
    bot.send_chat_action(chat_id, 'typing')
    time.sleep(4)
    bot.send_message(chat_id, "Posso falar dos meus conteúdos e das chamadas? 😈🔥")

@bot.message_handler(func=lambda message: True)
def control_flow(message):
    chat_id = message.chat.id
    if message.text == "/start": return
    step = user_steps.get(chat_id, 0)

    # PASSO 1 -> PASSO 2 (Início do convite)
    if step == 1:
        time.sleep(5)
        bot.send_chat_action(chat_id, 'upload_photo')
        try:
            with open('media/1.jpg', 'rb') as photo:
                bot.send_photo(chat_id, photo, caption="Eu vendo meu grupo vip com videos, fotos, videos personalizados.... punhetinha guiada... e muito mais amor ❤️")
        except: pass

        bot.send_chat_action(chat_id, 'record_voice')
        time.sleep(7)
        try:
            with open('media/1.ogg', 'rb') as voice:
                bot.send_voice(chat_id, voice)
        except: pass

        bot.send_chat_action(chat_id, 'typing')
        time.sleep(5)
        bot.send_message(chat_id, "Quer ver minha bucetinha amor? 😚❤️")
        user_steps[chat_id] = 2

    # PASSO 2 -> PASSO 3 (Amostra 1)
    elif step == 2:
        bot.send_chat_action(chat_id, 'typing')
        time.sleep(5)
        bot.send_message(chat_id, "Vou te mandar gatinho, mas não pode mostrar para ninguem em.... 😈")
        time.sleep(10)
        bot.send_chat_action(chat_id, 'upload_video')
        try:
            with open('media/1.mp4', 'rb') as video:
                bot.send_video(chat_id, video, caption="Pra você gatinho, espero que goste 🥰")
        except: pass

        time.sleep(4)
        bot.send_message(chat_id, "Quer ver mais?")
        user_steps[chat_id] = 3

    # PASSO 3 -> PASSO 4 (O Combo de Vídeos Amostra + Áudio + Oferta)
    elif step == 3:
        bot.send_chat_action(chat_id, 'typing')
        time.sleep(4)
        bot.send_message(chat_id, "🥰❤️❤️")
        time.sleep(5)
        bot.send_message(chat_id, "Vou te mandar uma amostra do meu grupinho vip só pq gostei de você.... vou confiar 🙈")
        time.sleep(10)
        # Envio dos 3 vídeos de amostra em sequência
        for i in range(1, 4): # vídeos media/amostra_1.mp4, amostra_2.mp4, amostra_3.mp4
            bot.send_chat_action(chat_id, 'upload_video')
            try:
                with open(f'media/amostra_{i}.mp4', 'rb') as v:
                    bot.send_video(chat_id, v)
                time.sleep(1)
            except: continue

        # Áudio "Vai me dar?"
        bot.send_chat_action(chat_id, 'record_voice')
        time.sleep(6)
        try:
            with open('media/2.ogg', 'rb') as v:
                bot.send_voice(chat_id, v)
        except: pass

        bot.send_chat_action(chat_id, 'typing')
        time.sleep(4)
        bot.send_message(chat_id, "Vai me dar? 😏💦")
        user_steps[chat_id] = 4

    # PASSO 4 -> PASSO 5 (Print do Canal e Fechamento)
    elif step == 4:
        bot.send_chat_action(chat_id, 'typing')
        time.sleep(5)
        bot.send_message(chat_id, "Safadinho... ☺️❤️")
        
        bot.send_chat_action(chat_id, 'typing')
        time.sleep(8)
        bot.send_message(chat_id, "Se voce virar meu cliente eu faço uma punheta guiada gemendo gostoso... pra você gozar pensando na minha bucetinha rosa 😈")
        
        bot.send_chat_action(chat_id, 'typing')
        time.sleep(6)
        bot.send_message(chat_id, "Posso fazer tudo isso para você por R$19,90 anjo, o grupo VIP + Punhetinha Guiada de 30 minutos ❤️")
        
        time.sleep(5)
        bot.send_message(chat_id, "Vai querer gatinho? 🔥")
        user_steps[chat_id] = 5

    # PASSO 5 -> GERAÇÃO DIRETA DE PIX (Com dados fixos)
    elif step == 5:
        # Áudio Final
        bot.send_chat_action(chat_id, 'record_voice')
        time.sleep(7)
        try:
            with open('media/3.ogg', 'rb') as v:
                bot.send_voice(chat_id, v)
        except: pass

        # Print do Canal
        bot.send_chat_action(chat_id, 'upload_photo')
        try:
            with open('media/grupo.jpg', 'rb') as photo:
                bot.send_photo(chat_id, photo, caption="Esse é o grupo que vou te colocar bb.... tem varios video la dentro... e todo dia posto video novo. Então o grupo existe sim amor")
        except: pass

        time.sleep(2)
        bot.send_message(chat_id, "Vou gerar minha chave pix pra você bb 😘🔥")
        time.sleep(2)
        bot.send_message(chat_id, "Gerando seu PIX... um segundinho... ⏳")
        
        res = create_alphapay_transaction(chat_id)
        if res and res.get('success'):
            data = res.get('data', {})
            pix_code = data.get('pix_code')
            tx_hash = data.get('hash')
            
            transaction_mapping[tx_hash] = chat_id
            
            bot.send_message(chat_id, "✅ Prontinho amor, gerei a chave pix!\n\n- Copie a Chave Pix \"copia e cola\" abaixo para realizar o pagamento ⤵️")
            time.sleep(2)
            bot.send_message(chat_id, f"`{pix_code}`", parse_mode="Markdown")
            
            time.sleep(4)
            bot.send_message(chat_id, "O acesso ao meu grupo vip com minhas fotos e videos são R$19,90 ta anjo?")
            time.sleep(4)
            bot.send_message(chat_id, "Assim que você pagar, eu te mando o link do grupo aqui na mesma hora! 🥰🥰❤️")
            user_steps[chat_id] = 9 # Aguardando pagamento
        else:
            bot.send_message(chat_id, "Tive um probleminha ao gerar o PIX 😔. Pode tentar novamente em alguns minutos?")
            user_steps[chat_id] = 5

    # PASSO 9 -> LEMBRETE DE PAGAMENTO
    elif step == 9:
        bot.send_message(chat_id, "Ainda estou aguardando o seu pagamento, anjo... o link já está prontinho aqui te esperando! 🥰")

if __name__ == "__main__":
    print("Alessandra online e convertendo...")
    
    # Limpa qualquer webhook anterior para evitar o erro 409 Conflict
    try:
        bot.remove_webhook()
        time.sleep(1)
    except:
        pass

    # Inicia o Flask em uma thread separada para ouvir o Webhook
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Inicia o polling do Bot
    bot.polling(non_stop=True)