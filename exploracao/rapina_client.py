# exploracao/rapina_client.py (VERSÃO FINAL COM RESPOSTA HIERÁRQUICA E TTS)

import cv2
import numpy as np
import requests
import base64
import pyttsx3 # Biblioteca para Texto-para-Fala (Text-to-Speech)

# --- INICIALIZAÇÃO DO MOTOR DE VOZ ---
try:
    engine = pyttsx3.init()
    # Opcional: Tenta obter vozes em Português do Brasil para uma melhor qualidade
    voices = engine.getProperty('voices')
    for voice in voices:
        if "brazil" in voice.id.lower():
            engine.setProperty('voice', voice.id)
            break
except Exception as e:
    print(f"Aviso: Não foi possível inicializar o motor de voz otimizado: {e}")
    engine = None

def falar_texto(texto: str):
    """Usa o motor de TTS para falar um texto em voz alta."""
    if engine:
        print(f"\n🔊 SHAULA (Áudio): {texto}")
        engine.say(texto)
        engine.runAndWait()
    else:
        print("\n[AVISO] Motor de voz não inicializado. A resposta de áudio não pode ser reproduzida.")

# --- FUNÇÕES DE VISÃO COMPUTACIONAL ---

def inicializar_cameras():
    cam_frontal = cv2.VideoCapture(0) 
    cam_olho = cv2.VideoCapture(1)

    if not cam_frontal.isOpened() or not cam_olho.isOpened():
        print("Erro: Não foi possível aceder a uma ou ambas as câmaras.")
        print("Dica: Verifica se as webcams estão conectadas e se não estão a ser usadas por outro programa.")
        return None, None
    
    print("Câmaras inicializadas com sucesso.")
    return cam_frontal, cam_olho

def detectar_foco_do_olhar(frame_olho):
    gray = cv2.cvtColor(frame_olho, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)

    # Ajusta este valor (entre 30 e 60) dependendo da iluminação do teu ambiente
    limiar_de_cinza = 40
    _, threshold = cv2.threshold(gray, limiar_de_cinza, 255, cv2.THRESH_BINARY_INV)

    contornos, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contornos:
        maior_contorno = max(contornos, key=cv2.contourArea)
        
        M = cv2.moments(maior_contorno)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            centro_pupila = (cx, cy)
            
            cv2.circle(frame_olho, centro_pupila, 10, (0, 255, 0), 2)
            return centro_pupila

    h, w, _ = frame_olho.shape
    return (w // 2, h // 2)

def mapear_e_capturar(posicao_pupila, frame_frontal, frame_olho):
    h_olho, w_olho, _ = frame_olho.shape
    h_frontal, w_frontal, _ = frame_frontal.shape
    
    foco_x_centro = int((w_olho - posicao_pupila[0]) * (w_frontal / w_olho))
    foco_y_centro = int(posicao_pupila[1] * (h_frontal / h_olho))

    foco_w, foco_h = 200, 200
    foco_x = foco_x_centro - foco_w // 2
    foco_y = foco_y_centro - foco_h // 2
    
    foco_x = np.clip(foco_x, 0, w_frontal - foco_w)
    foco_y = np.clip(foco_y, 0, h_frontal - foco_h)

    area_de_foco_recortada = frame_frontal[foco_y:foco_y+foco_h, foco_x:foco_x+foco_w]
    
    cv2.rectangle(frame_frontal, (foco_x, foco_y), (foco_x + foco_w, foco_y + foco_h), (0, 255, 255), 2)
    
    return area_de_foco_recortada

def enviar_para_analise(imagem_foco, pergunta_usuario, user_id, shaula_api_url="http://127.0.0.1:8000/rapina/analisar"):
    _, buffer = cv2.imencode('.jpg', imagem_foco)
    imagem_base64 = base64.b64encode(buffer).decode('utf-8')

    payload = { "imagem_base64": imagem_base64, "pergunta": pergunta_usuario, "user_id": user_id }

    try:
        print("A enviar imagem para análise da Shaula...")
        response = requests.post(shaula_api_url, json=payload)
        response.raise_for_status()
        print("Resposta recebida!")
        return response.json() 
    except requests.exceptions.RequestException as e:
        return {"resposta_visual": "Erro de API", "resposta_audio": f"Erro de comunicação: {e}"}

# --- LOOP PRINCIPAL DE EXECUÇÃO ---

def main():
    cam_frontal, cam_olho = inicializar_cameras()
    if cam_frontal is None:
        return

    USER_ID_ATUAL = "379c4b4d-625f-4e7a-b136-aedecae9ba50"

    while True:
        ret_frontal, frame_frontal = cam_frontal.read()
        ret_olho, frame_olho = cam_olho.read()

        if not ret_frontal or not ret_olho:
            print("Erro: Não foi possível ler o frame de uma das câmaras.")
            break

        frame_olho = cv2.flip(frame_olho, 1)
        posicao_pupila = detectar_foco_do_olhar(frame_olho)
        area_de_foco = mapear_e_capturar(posicao_pupila, frame_frontal, frame_olho)

        cv2.imshow("Visao frontal (Pressione ESPACO para Analisar)", frame_frontal)
        cv2.imshow("Visao do Olho", frame_olho)

        key = cv2.waitKey(1) & 0xFF

        if key == 32: # Barra de espaço
            print("\n[COMANDO RECEBIDO] Barra de espaço pressionada!")
            pergunta = "Shaula, o que é isto? Descreve-o detalhadamente."
            
            respostas = enviar_para_analise(area_de_foco, pergunta, USER_ID_ATUAL)
            
            resposta_visual = respostas.get("resposta_visual", "---")
            resposta_audio = respostas.get("resposta_audio", "Ocorreu um erro.")

            # --- PROCESSAMENTO HIERÁRQUICO ---
            # 1. Mostra a resposta curta no "visor" (o nosso terminal)
            print("\n------------------------------------")
            print(f"  VISOR DOS ÓCULOS: {resposta_visual}")
            print("------------------------------------")

            # 2. Fala a resposta detalhada no "ponto de escuta" (os teus fones/colunas)
            falar_texto(resposta_audio)

        elif key == ord('q'):
            break

    cam_frontal.release()
    cam_olho.release()
    cv2.destroyAllWindows()
    print("Programa encerrado.")

if __name__ == "__main__":
    main()