# ferramentas.py

import datetime
import cv2
import numpy as np
import base64
from typing import Callable

def verificar_hora_atual():
    agora = datetime.datetime.now()
    return f"A hora atual é {agora.strftime('%H:%M')} do dia {agora.strftime('%d/%m/%Y')}."

def descrever_o_que_vejo(pergunta_usuario: str) -> dict:
    """
    Usa OpenCV para detectar o objeto de cor mais proeminente no centro,
    destacá-lo com um retângulo e focar a pergunta do LLM nesse objeto.
    """
    print("[AÇÃO] Ativando a webcam para uma captura com FOCO INTELIGENTE...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return {"status": "error", "message": "Não consegui acessar a webcam."}

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return {"status": "error", "message": "Não consegui capturar uma imagem."}

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, w, _ = frame.shape
    center_x, center_y = int(w / 2), int(h / 2)
    roi = hsv_frame[center_y - 30:center_y + 30, center_x - 30:center_x + 30]
    mask_value = cv2.inRange(roi, (0, 50, 50), (180, 255, 255))
    
    if cv2.countNonZero(mask_value) > 0:
        hue_mean = cv2.mean(roi[:,:,0], mask=mask_value)[0]
    else:
        hue_mean = 0

    hue_int = int(hue_mean)
    lower_bound = np.array([max(0, hue_int - 10), 50, 50], dtype=np.uint8)
    upper_bound = np.array([min(180, hue_int + 10), 255, 255], dtype=np.uint8)

    color_mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
    contours, _ = cv2.findContours(color_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
        prompt_foco = f"A imagem possui um objeto destacado por um retângulo verde. Foque sua análise APENAS nesse objeto e responda à pergunta do meu criador: '{pergunta_usuario}'"
    else:
        prompt_foco = f"Analise a imagem como um todo e responda: '{pergunta_usuario}'"

    _, buffer = cv2.imencode('.jpeg', frame)
    base64_image = base64.b64encode(buffer).decode('utf-8')

    return { "status": "success", "image_base64": base64_image, "prompt": prompt_foco }