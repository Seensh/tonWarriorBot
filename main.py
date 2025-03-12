import time
import pyautogui
import cv2
import numpy as np
import pygetwindow as gw
import mss  # Captura monitores específicos
import mss.tools

# Solicita o tempo de espera ao usuário
horas = int(input("Digite o número de horas para esperar após o clique: "))
minutos = int(input("Digite o número de minutos para esperar após o clique: "))
tempo_de_espera = (horas * 3600) + (minutos * 60)  # Converte para segundos

# Carrega as imagens dos botões
button_claim_template = cv2.imread('assets/claim.png', cv2.IMREAD_UNCHANGED)
button_ok_template = cv2.imread('assets/ok.png', cv2.IMREAD_UNCHANGED)  # Botão OK
button_start_template = cv2.imread('assets/start.png', cv2.IMREAD_UNCHANGED)  # Botão Start

def capturar_area_jogo():
    """Captura a área da janela do Telegram onde o jogo está rodando."""
    try:
        janela = gw.getWindowsWithTitle("Miniapp: Ton Warrior bot")[0]  # Pega a janela do Telegram
        x, y, largura, altura = janela.left, janela.top, janela.width, janela.height
        
        with mss.mss() as sct:
            monitores = sct.monitors  # Lista de monitores

            # Tenta usar o segundo monitor, senão usa o primeiro
            if len(monitores) > 1:
                print("Capturando no segundo monitor...")
                monitor = monitores[1]  # Segundo monitor
            else:
                print("Segundo monitor não detectado! Usando o primeiro monitor...")
                monitor = monitores[0]  # Primeiro monitor

            # Ajusta a posição da captura dentro do monitor escolhido
            regiao = {
                "top": y, 
                "left": x, 
                "width": largura, 
                "height": altura
            }
            
            screenshot = sct.grab(regiao)
            screenshot_np = np.array(screenshot)  # Converte para NumPy array

            return screenshot_np, x, y
    except IndexError:
        print("Telegram não encontrado. Verificando novamente em 10 segundos...")
        return None, 0, 0  # Retorna None para indicar erro

def encontrar_botao(template):
    """Encontra a posição do botão na tela baseado no template fornecido."""
    screenshot_np, x_offset, y_offset = capturar_area_jogo()
    
    if screenshot_np is None:
        return []  # Retorna lista vazia se não conseguir capturar a tela

    # Converte a captura e o botão para escala de cinza
    screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
    button_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # Tenta encontrar o botão na tela
    resultado = cv2.matchTemplate(screenshot_gray, button_gray, cv2.TM_CCOEFF_NORMED)

    limiar = 0.6  # Reduzido para aumentar a chance de detecção
    locais = np.where(resultado >= limiar)

    return [(x + x_offset, y + y_offset) for x, y in zip(*locais[::-1])]

def clicar_no_botao(template, descricao):
    """Procura e clica no botão especificado pelo template."""
    locais = encontrar_botao(template)
    
    if locais:
        x, y = locais[0]  # Pega a primeira ocorrência encontrada
        pyautogui.moveTo(x + 10, y + 10, duration=0.2)
        pyautogui.click()
        print(f"{descricao} clicado em {x}, {y}!")
        return True  # Retorna True se clicou
    
    return False  # Retorna False se não encontrou o botão

# Loop principal
while True:
    print("Procurando botão CLAIM...")
    
    # Continua verificando até encontrar e clicar no botão "Claim"
    while not clicar_no_botao(button_claim_template, "Botão CLAIM"):
        time.sleep(10)  # Aguarda 10 segundos antes de verificar de novo
    
    # Espera 0.5 segundo antes de procurar o botão "OK"
    time.sleep(0.5)

    print("Procurando botão OK...")
    
    # Continua verificando até encontrar e clicar no botão "OK"
    while not clicar_no_botao(button_ok_template, "Botão OK"):
        time.sleep(1)  # Aguarda 1 segundo antes de verificar de novo
    
    # Aguarda 6 segundos antes de clicar no botão "Start"
    time.sleep(6)

    print("Procurando botão START...")
    
    # Continua verificando até encontrar e clicar no botão "Start"
    while not clicar_no_botao(button_start_template, "Botão START"):
        time.sleep(1)  # Aguarda 1 segundo antes de verificar de novo

    print(f"Aguardando {horas} horas e {minutos} minutos antes de procurar novamente...")
    time.sleep(tempo_de_espera)  # Aguarda o tempo definido antes de repetir o ciclo
