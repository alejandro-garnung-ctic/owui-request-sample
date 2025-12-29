#!/usr/bin/env python3
"""
Script para enviar prompt + imagen codificada en base64 a modelos multimodales
usando chat completions.

Uso:
    python test_multimodal_model.py --model <modelo> --prompt "Texto aquí" --image <ruta_imagen>
"""

import os
import sys
import argparse
import base64
import requests
import dotenv

dotenv.load_dotenv()

API_URL = os.getenv("CHAT_COMPLETIONS_API_URL", "http://localhost:8000/v1/chat/completions")
API_TOKEN = os.getenv("CHAT_COMPLETIONS_API_TOKEN", "")

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def chat_multimodal(model_name, prompt, image_path):
    image_base64 = encode_image_to_base64(image_path)

    headers = {
        "Content-Type": "application/json",
    }
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"

    # Payload en formato chat completions con imagen embebida en base64
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1024,
        "temperature": 0.7
    }

    response = requests.post(API_URL, json=payload, headers=headers, timeout=120)
    if response.status_code != 200:
        print(f"ERROR {response.status_code}: {response.text}")
        return None

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error leyendo respuesta JSON: {e}")
        print(data)
        return None

def main():
    parser = argparse.ArgumentParser(description="Prueba chat completions multimodal con imagen")
    parser.add_argument("--model", required=True, help="Nombre del modelo")
    parser.add_argument("--prompt", required=True, help="Prompt de texto")
    parser.add_argument("--image", required=True, help="Ruta de la imagen (png/jpg)")

    args = parser.parse_args()

    if not os.path.isfile(args.image):
        print(f"❌ No se encontró la imagen: {args.image}")
        sys.exit(1)

    print(f"Consultando modelo: {args.model}")
    print(f"Prompt:\n{args.prompt}\n")
    print(f"Imagen: {args.image}")

    result = chat_multimodal(args.model, args.prompt, args.image)

    if result:
        print("\nRespuesta del modelo:")
        print(result)
    else:
        print("No se recibió respuesta válida")

if __name__ == "__main__":
    main()
