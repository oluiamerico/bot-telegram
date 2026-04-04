import telebot
import time
import os
import requests
import threading
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# ==========================================
# ⚙️ CONFIGURAÇÕES INICIAIS E VARIÁVEIS
# ==========================================
load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Configurações AlphaPay e Grupo
ALPHAPAY_TOKEN = os.getenv('ALPHAPAY_TOKEN')
PRODUCT_HASH = os.getenv('PRODUCT_HASH')
OFFER_HASH = os.getenv('OFFER_HASH')
GROUP_LINK = os.getenv('GROUP_LINK')
GROUP_ID = os.getenv('GROUP_ID')

# Estados globais (Em memória)
user_steps = {}           # Passo atual de cada usuário no funil
processing_users = set()  # Trava para evitar mensagens duplicadas durante o envio de mídias

# Mapeamentos e Leads (Persistentes)
transaction_mapping = {}  # {hash_da_transacao: chat_id}
leads_data = {}           # {chat_id: {pix_code, start_time, reminders}}

DATA_FILE = "transactions.json"
LEADS_FILE = "leads.json"

# ==========================================
# 💾 GESTÃO DE PERSISTÊNCIA (JSON)
# ==========================================
def save_data():
    """Salva os dados de transações e leads em arquivos locais."""
    with open(DATA_FILE, 'w') as f:
        json.dump(transaction_mapping, f)
    with open(LEADS_FILE, 'w') as f:
        json.dump(leads_data, f)

def load_data():
    """Carrega os dados salvos anteriormente para evitar perda de leads."""
    global transaction_mapping, leads_data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                transaction_mapping = json.load(f)
        except: transaction_mapping = {}
    if os.path.exists(LEADS_FILE):
        try:
            with open(LEADS_FILE, 'r') as f:
                leads_data = json.load(f)
        except: leads_data = {}

# ==========================================
# 💳 INTEGRAÇÃO COM GATEWAY ALPHAPAY
# ==========================================
def create_alphapay_transaction(chat_id):
    """Faz a chamada para a API da AlphaPay para gerar o PIX."""
    postback_url = os.getenv('POSTBACK_URL')
    if not postback_url or postback_url == "None":
        postback_url = "https://google.com/webhook-placeholder"

    payload = {
        "amount": 1990, # Valor fixo: R$ 19,90
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
        "postback_url": postback_url
    }
    
    url = f"https://api.alphapaybrasil.com.br/api/public/v1/transactions?api_token={ALPHAPAY_TOKEN}"
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"DEBUG Error AlphaPay: {e}")
        return None

# ==========================================
# 🔄 SISTEMA DE REMARKETING (LEMBRETES)
# ==========================================
def reminder_worker():
    """
    Monitora leads que geraram PIX mas não pagaram.
    Intervalos: 7 minutos, 30 minutos, 1 hora.
    """
    intervals = [420, 1800, 3600]
    
    while True:
        time.sleep(30) # Checagem a cada 30 segundos
        now = time.time()
        to_remove = []
        
        for chat_id, data in list(leads_data.items()):
            reminders_sent = data.get('reminders', 0)
            
            if reminders_sent >= len(intervals):
                to_remove.append(chat_id)
                continue
            
            target_elapsed = intervals[reminders_sent]
            
            if now - data['start_time'] >= target_elapsed:
                try:
                    data['reminders'] = reminders_sent + 1
                    
                    if data['reminders'] == 1: # 7 min
                        bot.send_message(chat_id, "Oi amor... ainda estou te esperando 🥰. O seu login do grupo VIP já está quase pronto, você ainda quer? 😈🔥")
                    elif data['reminders'] == 2: # 30 min
                        bot.send_message(chat_id, "Poxa bb, você sumiu... 🥺. Vou segurar o valor de R$19,90 por mais um tempinho pra você, tá? Aproveita que postei coisa nova no grupo!")
                        time.sleep(2)
                        bot.send_message(chat_id, f"Aqui está sua chave PIX de novo pra facilitar:\n`{data['pix_code']}`", parse_mode="Markdown")
                    elif data['reminders'] == 3: # 60 min
                        bot.send_message(chat_id, "Última chance de virar meu cliente VIP e ver tudo sem censura! ❤️🔥. Depois desse convite, vou ter que liberar sua vaga... vai perder?")
                    
                    save_data()
                except Exception as e:
                    print(f"DEBUG Error reminder ({data['reminders']}) for {chat_id}: {e}")
        
        for cid in to_remove:
            if cid in leads_data: del leads_data[cid]
        if to_remove: save_data()

# ==========================================
# 🛰️ SERVIDOR DE WEBHOOK (RECEPÇÃO DE PAGAMENTOS)
# ==========================================
app = Flask(__name__)

@app.route('/webhook/alphapay', methods=['POST'])
def alphapay_webhook():
    """Recebe as notificações de pagamento da AlphaPay."""
    content = request.json
    print(f"DEBUG: Webhook recebido: {json.dumps(content)}")
    
    if content and content.get('status') == 'paid':
        tx_hash = content.get('transaction_hash') or content.get('hash') or content.get('transaction')
        chat_id = transaction_mapping.get(str(tx_hash))
        
        if chat_id:
            user_id_str = str(chat_id)
            if user_id_str in leads_data:
                del leads_data[user_id_str]
                save_data()
            
            chat_id_int = int(chat_id)
            bot.send_message(chat_id_int, "✅ Pagemento confirmado, meu amor! ❤️")
            time.sleep(2)
            
            # Gera Link Único se o GROUP_ID estiver configurado
            link_to_send = GROUP_LINK
            if GROUP_ID:
                try:
                    invite = bot.create_chat_invite_link(chat_id=GROUP_ID, member_limit=1)
                    link_to_send = invite.invite_link
                except Exception as e:
                    print(f"DEBUG Link Unique Error: {e}")

            bot.send_message(chat_id_int, f"Aqui está o link do seu acesso vitalício: {link_to_send}")
            bot.send_message(chat_id_int, "Seja muito bem-vindo(a) ao meu mundinho VIP! 😈🔥")
            user_steps[chat_id_int] = 0
            
    return jsonify({"status": "ok"}), 200

def run_flask():
    """Inicia o servidor Flask na porta fornecida pelo Railway."""
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# ==========================================
# 🤖 LÓGICA DO TELEGRAM (HANDLERS)
# ==========================================

@bot.message_handler(commands=['start'])
def start(message):
    """Comando inicial: inicia o funil de vendas."""
    chat_id = message.chat.id
    user_steps[chat_id] = 1
    time.sleep(5)
    bot.send_chat_action(chat_id, 'typing')
    time.sleep(5)
    bot.send_message(chat_id, "oi gatinho")
    
    bot.send_chat_action(chat_id, 'typing')
    time.sleep(6)
    bot.send_message(chat_id, "Me chamo Sofia, tenho 24 aninhos... prazer 😉")
    
    bot.send_chat_action(chat_id, 'typing')
    time.sleep(4)
    bot.send_message(chat_id, "Posso falar dos meus conteúdos? 😈🔥")

@bot.message_handler(func=lambda message: True)
def control_flow(message):
    """Gerenciador principal do fluxo de vendas (Máquina de Estados)."""
    chat_id = message.chat.id
    if message.text == "/start": return
    step = user_steps.get(chat_id, 0)
    print(f"DEBUG: Msg de {chat_id}: '{message.text}' (Passo: {step})")

    # Trava de processamento para evitar duplicidade
    if chat_id in processing_users:
        print(f"DEBUG: Ignorando duplicado de {chat_id}")
        return
    
    processing_users.add(chat_id)
    
    try:
        # PASSO 1 -> 2: Primeira Foto e Áudio de apresentação
        if step == 1:
            user_steps[chat_id] = 2
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

        # PASSO 2 -> 3: Primeiro Vídeo Amostra
        elif step == 2:
            user_steps[chat_id] = 3
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

        # PASSO 3 -> 4: Combo de Vídeos Amostra + Áudio "Vai me dar?"
        elif step == 3:
            user_steps[chat_id] = 4
            bot.send_chat_action(chat_id, 'typing')
            time.sleep(4)
            bot.send_message(chat_id, "🥰❤️❤️")
            time.sleep(5)
            bot.send_message(chat_id, "Vou te mandar uma amostra do meu grupinho vip só pq gostei de você.... vou confiar 🙈")
            time.sleep(10)
            for i in range(1, 4): # amostra_1.mp4, amostra_2.mp4, amostra_3.mp4
                bot.send_chat_action(chat_id, 'upload_video')
                try:
                    with open(f'media/amostra_{i}.mp4', 'rb') as v:
                        bot.send_video(chat_id, v)
                    time.sleep(1)
                except: continue

            bot.send_chat_action(chat_id, 'record_voice')
            time.sleep(6)
            try:
                with open('media/2.ogg', 'rb') as v:
                    bot.send_voice(chat_id, v)
                time.sleep(1)
            except: pass

            bot.send_chat_action(chat_id, 'typing')
            time.sleep(4)
            bot.send_message(chat_id, "Vai me dar? 😏💦")

        # PASSO 4 -> 5: Oferta do VIP e Print do Canal
        elif step == 4:
            user_steps[chat_id] = 5
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

        # PASSO 5: Geração de PIX e Início do Remarketing
        elif step == 5:
            user_id_str = str(chat_id)
            user_steps[chat_id] = 9
            
            bot.send_chat_action(chat_id, 'record_voice')
            time.sleep(7)
            try:
                with open('media/3.ogg', 'rb') as v:
                    bot.send_voice(chat_id, v)
            except: pass
            time.sleep(8)

            bot.send_chat_action(chat_id, 'upload_photo')
            try:
                with open('media/grupo.png', 'rb') as photo:
                    bot.send_photo(chat_id, photo, caption="Esse é o grupo que vou te colocar bb.... tem varios video la dentro... e todo dia posto video novo.")
            except: pass

            time.sleep(9)
            bot.send_message(chat_id, "Vou gerar minha chave pix pra você bb 😘🔥")
            time.sleep(9)
            bot.send_message(chat_id, "Gerando seu PIX... um segundinho... ⏳")
            
            res = create_alphapay_transaction(chat_id)
            if res and (res.get('success') or 'pix' in res or 'data' in res):
                pix_data = res.get('pix', {})
                data_field = res.get('data', {})
                pix_code = pix_data.get('pix_qr_code') or data_field.get('pix_code')
                tx_hash = res.get('hash') or data_field.get('hash')
                
                if pix_code:
                    transaction_mapping[str(tx_hash)] = chat_id
                    
                    # INICIA MONITORAMENTO PARA REMARKETING
                    leads_data[user_id_str] = {
                        "pix_code": pix_code,
                        "start_time": time.time(),
                        "reminders": 0
                    }
                    save_data()
                    
                    bot.send_message(chat_id, "✅ Prontinho amor, gerei a chave pix!\n\n- Copie a Chave Pix \"copia e cola\" abaixo:")
                    time.sleep(3)
                    bot.send_message(chat_id, f"`{pix_code}`", parse_mode="Markdown")
                    
                    time.sleep(8)
                    bot.send_message(chat_id, "O acesso ao meu grupo vip com minhas fotos e videos são R$19,90 ta anjo?")
                    time.sleep(8)
                    bot.send_message(chat_id, "Assim que você pagar, eu te mando o link do grupo aqui na mesma hora! 🥰🥰❤️")
                else:
                    bot.send_message(chat_id, "Tive um probleminha ao gerar o código PIX 😔.")
                    user_steps[chat_id] = 5
            else:
                bot.send_message(chat_id, "Tive um erro ao gerar o PIX 😔. Pode tentar novamente?")
                user_steps[chat_id] = 5

        # PASSO 9: Aguardando Pagamento (Estático)
        elif step == 9:
            bot.send_message(chat_id, "Ainda estou aguardando o seu pagamento, anjo... o link já está prontinho aqui te esperando! 🥰")
            
    except Exception as e:
        print(f"DEBUG Error control_flow: {e}")
    finally:
        if chat_id in processing_users:
            processing_users.remove(chat_id)

# ==========================================
# 🚀 INICIALIZAÇÃO DO SISTEMA
# ==========================================
if __name__ == "__main__":
    print("Sofia online e convertendo...")
    load_data()
    
    try:
        bot.remove_webhook()
        time.sleep(1)
    except: pass

    # Inicia Webhook em segundo plano
    threading.Thread(target=run_flask, daemon=True).start()
    # Inicia Remarketing em segundo plano
    threading.Thread(target=reminder_worker, daemon=True).start()
    
    # Inicia escuta do Bot
    bot.polling(non_stop=True)