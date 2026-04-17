import os
import requests
import json
import random

def generate_cpf():
    cpf = [random.randint(0, 9) for x in range(9)]
    for _ in range(2):
        val = sum([(len(cpf) + 1 - i) * v for i, v in enumerate(cpf)]) % 11
        cpf.append(11 - val if val > 1 else 0)
    return ''.join(map(str, cpf))

env_vars = {}
with open(".env") as f:
    for line in f:
        if "=" in line:
            key, val = line.strip().split("=", 1)
            env_vars[key] = val

ALPHAPAY_TOKEN = env_vars.get('ALPHAPAY_TOKEN')
PRODUCT_HASH = env_vars.get('PRODUCT_HASH')
OFFER_HASH = env_vars.get('OFFER_HASH')

def test_payload(payload):
    url = f"https://api.alphapaybrasil.com.br/api/public/v1/transactions?api_token={ALPHAPAY_TOKEN}"
    try:
        response = requests.post(url, json=payload)
        print("Status code:", response.status_code)
        print("Response text:", response.text)
    except Exception as e:
        print(f"Error AlphaPay: {e}")

if __name__ == "__main__":
    postback_url = "https://discord.com"
    
    # Payload D - Different CPF and Email
    print("Testing original payload structure PIX capitalized, different email...")
    cpf = generate_cpf()
    print("Generated CPF:", cpf)
    payload_d = {
        "amount": 1990,
        "offer_hash": OFFER_HASH,
        "payment_method": "PIX",
        "customer": {
            "name": "João da Silva",
            "email": f"joao{random.randint(100,999)}@gmail.com",
            "phone_number": "11999999999",
            "document": cpf
        },
        "cart": [{
            "product_hash": PRODUCT_HASH,
            "title": "Grupo VIP",
            "price": 1990,
            "quantity": 1,
            "operation_type": 1,
            "tangible": False
        }],
        "transaction_origin": "api",
        "postback_url": postback_url
    }
    test_payload(payload_d)
    
    # Payload E - Pix lowercase, default original fields, but remove tangible
    print("\nTesting original payload, but tangible removed...")
    payload_e = {
        "amount": 1990,
        "offer_hash": OFFER_HASH,
        "payment_method": "pix",
        "customer": {
            "name": "Cliente Telegram",
            "email": "cliente@gmail.com",
            "phone_number": "11989283928",
            "document": cpf
        },
        "cart": [{
            "product_hash": PRODUCT_HASH,
            "title": "Grupo VIP",
            "price": 1990,
            "quantity": 1,
            "operation_type": 1
        }],
        "transaction_origin": "api",
        "postback_url": postback_url
    }
    test_payload(payload_e)
