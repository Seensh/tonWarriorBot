import time
import pyautogui
import cv2
import numpy as np
import pygetwindow as gw
import mss
import mss.tools

# Solicita o tempo de espera entre ciclos ao usuário
horas = int(input("Digite o número de horas para esperar após o clique: "))
minutos = int(input("Digite o número de minutos para esperar após o clique: "))
tempo_de_espera = (horas * 3600) + (minutos * 60)


# Pergunta ao usuário se o timer do Claim já está pronto
resposta = input("O botão Claim já está disponível? (s/n): ").strip().lower()

if resposta == "n":
    horas_faltando = int(input("Quantas horas faltam para o primeiro Claim? "))
    minutos_faltando = int(input("Quantos minutos faltam para o primeiro Claim? "))
    tempo_espera_inicial = (horas_faltando * 3600) + (minutos_faltando * 60)

    print(f"Aguardando {horas_faltando} horas e {minutos_faltando} minutos antes de iniciar o processo...")
    time.sleep(tempo_espera_inicial)

print("Iniciando o bot...")

# Carrega as imagens dos botões
button_claim_template = cv2.imread('assets/claim.png', cv2.IMREAD_UNCHANGED)
button_ok_template = cv2.imread('assets/ok.png', cv2.IMREAD_UNCHANGED)
button_start_template = cv2.imread('assets/start.png', cv2.IMREAD_UNCHANGED)
button_play_template = cv2.imread('assets/play.png', cv2.IMREAD_UNCHANGED)
power_zero_template = cv2.imread('assets/0percent.png', cv2.IMREAD_UNCHANGED)  # Verificação de energia

# Coordenadas RELATIVAS das abas dentro da janela do jogo
abas_relativas = [
    (55, 543),  # Aba 1
    (114, 540),  # Aba 2
    (177, 541),  # Aba 3
    (243, 541),  # Aba 4
    (301, 543),  # Aba 5
    (361, 540)   # Aba 6
]

def capturar_area_jogo():
    """Captura a área da janela do Telegram onde o jogo está rodando."""
    try:
        janela = gw.getWindowsWithTitle("Miniapp: Ton Warrior bot")[0]
        x_janela, y_janela, largura, altura = janela.left, janela.top, janela.width, janela.height
        
        with mss.mss() as sct:
            regiao = {"top": y_janela, "left": x_janela, "width": largura, "height": altura}
            screenshot = sct.grab(regiao)
            screenshot_np = np.array(screenshot)

            return screenshot_np, x_janela, y_janela
    except IndexError:
        print("Telegram não encontrado. Verificando novamente em 10 segundos...")
        return None, 0, 0

def encontrar_botao(template, limiar=0.8):
    """Encontra a posição do botão na tela baseado no template fornecido."""
    screenshot_np, x_janela, y_janela = capturar_area_jogo()
    
    if screenshot_np is None:
        return []

    screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
    button_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    resultado = cv2.matchTemplate(screenshot_gray, button_gray, cv2.TM_CCOEFF_NORMED)
    locais = np.where(resultado >= limiar)

    return [(x + x_janela, y + y_janela) for x, y in zip(*locais[::-1])]

def verificar_energia():
    """Verifica se há energia disponível antes de tentar clicar no Claim."""
    locais = encontrar_botao(power_zero_template, limiar=0.9)  # Ajustado para evitar falsos positivos
    if locais:
        print("⚡ [SEM ENERGIA] 0% detectado! Pulando esta aba...")
        return False
    return True

def clicar_no_botao(template, descricao):
    """Procura e clica no botão especificado pelo template."""
    locais = encontrar_botao(template)
    
    if locais:
        x, y = locais[0]
        pyautogui.moveTo(x + 10, y + 10, duration=0.5)
        pyautogui.click()
        print(f"{descricao} clicado em {x}, {y}!")
        return True
    
    return False

def processar_aba(x_janela, y_janela):
    """Executa a sequência de cliques para uma aba."""
    print("Procurando botão CLAIM...")

    if not verificar_energia():
        return  # Se não houver energia, não tenta clicar no Claim

    # Tenta encontrar o botão Claim
    while not clicar_no_botao(button_claim_template, "Botão CLAIM"):
        print("Botão CLAIM não encontrado. Verificando se é necessário clicar no botão PLAY...")
        
        # Se o botão "Claim" não for encontrado, tenta clicar no botão "Play"
        if clicar_no_botao(button_play_template, "Botão PLAY"):
            print("Botão PLAY clicado. Esperando 10 segundos para carregar...")
            time.sleep(10)  # Espera o jogo carregar
            
            # Depois de clicar em Play, tenta novamente encontrar o botão Claim
            continue
        
        print("Nenhum botão Claim encontrado e botão Play não apareceu. Pulando esta aba.")
        return  # Se não encontrar Play nem Claim, sai dessa aba

    time.sleep(1)

    print("Procurando botão OK...")
    
    while not clicar_no_botao(button_ok_template, "Botão OK"):
        time.sleep(2)
    
    time.sleep(5)

    print("Procurando botão START...")
    
    while not clicar_no_botao(button_start_template, "Botão START"):
        time.sleep(5)

# Loop principal
while True:
    try:
        janela = gw.getWindowsWithTitle("Miniapp: Ton Warrior bot")[0]
        x_janela, y_janela = janela.left, janela.top
    except IndexError:
        print("Janela do jogo não encontrada. Tentando novamente em 10 segundos...")
        time.sleep(10)
        continue

    for i, (x_rel, y_rel) in enumerate(abas_relativas):
        x_aba = x_janela + x_rel
        y_aba = y_janela + y_rel
        time.sleep(2)
        print(f"Alternando para a aba {i + 1}...")
        pyautogui.moveTo(x_aba, y_aba, duration=0.5)
        pyautogui.click()
        time.sleep(6)

        processar_aba(x_janela, y_janela)

    print(f"Aguardando {horas} horas e {minutos} minutos antes de repetir o processo...")
    time.sleep(tempo_de_espera)
