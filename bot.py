import telebot
import time
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

user_steps = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
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

@bot.message_handler(func=lambda message: True)
def control_flow(message):
    chat_id = message.chat.id
    if message.text == "/start": return
    step = user_steps.get(chat_id, 0)

    # PASSO 1 -> PASSO 2 (Início do convite)
    if step == 1:
        bot.send_chat_action(chat_id, 'upload_photo')
        try:
            with open('media/1.jpg', 'rb') as photo:
                bot.send_photo(chat_id, photo, caption="Eu vendo meu grupo vip com videos, fotos, videos personalizados.... punhetinha guiada... e muito mais amor ❤️")
        except: pass

        bot.send_chat_action(chat_id, 'record_voice')
        time.sleep(4)
        try:
            with open('media/1.ogg', 'rb') as voice:
                bot.send_voice(chat_id, voice)
        except: pass

        bot.send_chat_action(chat_id, 'typing')
        time.sleep(2)
        bot.send_message(chat_id, "Quer ver minha bucetinha amor? 😚❤️")
        user_steps[chat_id] = 2

    # PASSO 2 -> PASSO 3 (Amostra 1)
    elif step == 2:
        bot.send_chat_action(chat_id, 'typing')
        time.sleep(2)
        bot.send_message(chat_id, "Vou te mandar gatinho, mas não pode mostrar para ninguem em.... 😈")
        
        bot.send_chat_action(chat_id, 'upload_video')
        try:
            with open('media/1.webm', 'rb') as video:
                bot.send_video(chat_id, video, caption="Pra você gatinho, espero que goste 🥰")
        except: pass

        time.sleep(2)
        bot.send_message(chat_id, "Quer ver mais?")
        user_steps[chat_id] = 3

    # PASSO 3 -> PASSO 4 (O Combo de Vídeos Amostra + Áudio + Oferta)
    elif step == 3:
        bot.send_chat_action(chat_id, 'typing')
        time.sleep(1)
        bot.send_message(chat_id, "🥰❤️❤️")
        bot.send_message(chat_id, "Vou te mandar uma amostra do meu grupinho vip só pq gostei de você.... vou confiar 🙈")
        
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
        time.sleep(3)
        try:
            with open('media/2.ogg', 'rb') as v:
                bot.send_voice(chat_id, v)
        except: pass

        bot.send_chat_action(chat_id, 'typing')
        time.sleep(2)
        bot.send_message(chat_id, "Vai me dar? 😏💦")
        user_steps[chat_id] = 4

    # PASSO 4 -> PASSO 5 (Print do Canal e Fechamento)
    elif step == 4:
        bot.send_chat_action(chat_id, 'typing')
        time.sleep(2)
        bot.send_message(chat_id, "Safadinho... ☺️❤️")
        
        bot.send_chat_action(chat_id, 'typing')
        time.sleep(3)
        bot.send_message(chat_id, "Se voce virar meu cliente eu faço uma punheta guiada gemendo gostoso... pra você gozar pensando na minha bucetinha rosa 😈")
        
        bot.send_chat_action(chat_id, 'typing')
        time.sleep(2)
        bot.send_message(chat_id, "Posso fazer tudo isso para você por R$19,90 anjo, o grupo VIP + Punhetinha Guiada de 30 minutos ❤️")
        
        bot.send_message(chat_id, "Vai querer gatinho? 🔥")
        user_steps[chat_id] = 5

    # PASSO 5 -> FINAL (Geração do Pix com Print do Canal)
    elif step == 5:
        # Áudio Final
        bot.send_chat_action(chat_id, 'record_voice')
        time.sleep(4)
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
        
        bot.send_chat_action(chat_id, 'typing')
        time.sleep(2)
        bot.send_message(chat_id, "✅ Prontinho amor, gerei a chave pix!\n\n- Copie a Chave Pix \"copia e cola\" abaixo para realizar o pagamento ⤵️")
        
        # Sua chave PIX real (substituída pela da imagem)
        bot.send_message(chat_id, "00020101021226810014br.gov.bcb.pix2559qr.woovi.com/qr/v2/cob/6454384b-36d9-48e8-861b-36276c5ea40e520400005303986540519.905802BR5909PUSHINPAY6011HORTOLANDIA62290525f24d170d57724805ada1ae08c6304D647")
        
        bot.send_message(chat_id, "O acesso ao meu grupo vip com minhas fotos e videos são R$19,90 ta anjo?")
        bot.send_message(chat_id, "vou te mandar o link do grupo assim que realizar o pagamento 🥰🥰❤️")
        bot.send_message(chat_id, "Você só paga uma vez e tem acesso vitalício ❤️")
        user_steps[chat_id] = 0

print("Alessandra online e convertendo...")
bot.polling(non_stop=True)