import telebot
import time

# Substitua pelo seu Token do @BotFather
TOKEN = '8696967580:AAH25QeL3C3WLXxalYOePzhtvsxytaVEdN8'
bot = telebot.TeleBot(TOKEN)

# Dicionário na memória para controlar o fluxo
user_steps = {}

# --- FUNÇÃO DE INÍCIO (Gatilho /start) ---
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    # Resetamos o passo do usuário para o início sempre que ele der /start
    user_steps[chat_id] = 1
    
    bot.send_chat_action(chat_id, 'typing')
    time.sleep(2)
    bot.send_message(chat_id, "oi gatinho")
    
    bot.send_chat_action(chat_id, 'typing')
    time.sleep(3)
    bot.send_message(chat_id, "Me chamo Alessandra, tenho 19 aninhos... prazer 😉")
    
    bot.send_chat_action(chat_id, 'typing')
    time.sleep(2)
    bot.send_message(chat_id, "Posso falar dos meus conteúdos e das chamadas? 😈🔥")

# --- FUNÇÃO DE FLUXO (Qualquer outra resposta) ---
@bot.message_handler(func=lambda message: True)
def control_flow(message):
    chat_id = message.chat.id
    
    # Se o usuário digitar /start, ignoramos nesta função para não duplicar a resposta
    if message.text == "/start":
        return

    step = user_steps.get(chat_id, 0)

    # PASSO 1 -> PASSO 2 (Apresentação do VIP e Áudio)
    if step == 1:
        bot.send_chat_action(chat_id, 'upload_photo')
        try:
            with open('media/tabela_vip.jpg', 'rb') as photo:
                bot.send_photo(chat_id, photo, caption="Eu vendo meu grupo vip com videos, fotos, videos personalizados.... punhetinha guiada... e muito mais amor ❤️")
        except:
            bot.send_message(chat_id, "Eu vendo meu grupo vip com videos, fotos... ❤️")

        bot.send_chat_action(chat_id, 'record_voice')
        time.sleep(4)
        try:
            with open('media/audio_apresentacao.ogg', 'rb') as voice:
                bot.send_voice(chat_id, voice)
        except:
            pass

        bot.send_chat_action(chat_id, 'typing')
        time.sleep(2)
        bot.send_message(chat_id, "Quer ver minha bucetinha amor? 😚❤️")
        user_steps[chat_id] = 2

    # PASSO 2 -> PASSO 3 (Primeira Amostra de Vídeo)
    elif step == 2:
        bot.send_chat_action(chat_id, 'typing')
        time.sleep(2)
        bot.send_message(chat_id, "Vou te mandar gatinho, mas não pode mostrar para ninguem em.... 😈")
        
        bot.send_chat_action(chat_id, 'upload_video')
        try:
            with open('media/amostra_quente.mp4', 'rb') as video:
                bot.send_video(chat_id, video, caption="Pra você gatinho, espero que goste 🥰")
        except:
            bot.send_message(chat_id, "Pra você gatinho, espero que goste 🥰")

        time.sleep(2)
        bot.send_message(chat_id, "Quer ver mais?")
        user_steps[chat_id] = 3

    # PASSO 3 -> PASSO 4 (Print do Canal e Oferta)
    elif step == 3:
        bot.send_chat_action(chat_id, 'typing')
        time.sleep(2)
        bot.send_message(chat_id, "🥰❤️❤️")
        bot.send_message(chat_id, "Vou te mandar uma amostra do meu grupinho vip só pq gostei de você.... vou confiar 🙈")
        
        try:
            with open('media/print_canal.jpg', 'rb') as photo:
                bot.send_photo(chat_id, photo, caption="Esse é o grupo que vou te colocar bb.... tem varios video la dentro... e todo dia posto video novo.")
        except:
            pass

        bot.send_chat_action(chat_id, 'typing')
        time.sleep(3)
        bot.send_message(chat_id, "Se voce virar meu cliente eu faço uma punheta guiada gemendo gostoso... pra você gozar pensando na minha bucetinha rosa 😈")
        
        bot.send_chat_action(chat_id, 'typing')
        time.sleep(2)
        bot.send_message(chat_id, "Posso fazer tudo isso para você por R$20,00 anjo, o grupo VIP + Punhetinha Guiada de 30 minutos ❤️")
        
        bot.send_message(chat_id, "Vai querer gatinho? 🔥")
        user_steps[chat_id] = 4

    # PASSO 4 -> FINAL (Geração do Pix)
    elif step == 4:
        bot.send_chat_action(chat_id, 'typing')
        time.sleep(2)
        bot.send_message(chat_id, "Vou gerar minha chave pix pra você bb 😘🔥")
        
        bot.send_message(chat_id, "✅ Prontinho amor, gerei a chave pix!\n\n- Copie a Chave Pix \"copia e cola\" abaixo para realizar o pagamento ⤵️")
        
        # Chave estática (substitua pela sua ou lógica de API futura)
        bot.send_message(chat_id, "00020101021126580014br.gov.bcb.pix0136...")
        
        bot.send_message(chat_id, "O acesso ao meu grupo vip com minhas fotos e videos são R$20,00 ta anjo?")
        bot.send_message(chat_id, "vou te mandar o link do grupo assim que realizar o pagamento 🥰🥰❤️")
        bot.send_message(chat_id, "Você só paga uma vez e tem acesso vitalício ❤️")
        
        # Reseta o fluxo para que o usuário possa recomeçar se quiser
        user_steps[chat_id] = 0

print("Alessandra está online e pronta para converter...")
bot.polling(non_stop=True)