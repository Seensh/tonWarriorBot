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

# Tempo para verificar o botão "Claim" a cada 2 horas
tempo_verificacao = 2 * 3600  # 2 horas em segundos
ultimo_teste = time.time()

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
    (305, 543),  # Aba 5
    (378, 540)   # Aba 6
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

def encontrar_botao(template):
    """Encontra a posição do botão na tela baseado no template fornecido."""
    screenshot_np, x_janela, y_janela = capturar_area_jogo()
    
    if screenshot_np is None:
        return []

    screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
    button_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    resultado = cv2.matchTemplate(screenshot_gray, button_gray, cv2.TM_CCOEFF_NORMED)
    limiar = 0.6
    locais = np.where(resultado >= limiar)

    return [(x + x_janela, y + y_janela) for x, y in zip(*locais[::-1])]

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

def verificar_energia():
    """Verifica se há energia disponível na aba atual antes de tentar clicar no Claim."""
    if encontrar_botao(power_zero_template):
        print("🔋 Sem energia! Pulando esta aba...")
        return False
    return True

def verificar_todas_abas(x_janela, y_janela):
    """Verifica todas as abas para ver se há um botão Claim disponível e inicia o ciclo se encontrar."""
    for i, (x_rel, y_rel) in enumerate(abas_relativas):
        x_aba = x_janela + x_rel
        y_aba = y_janela + y_rel

        pyautogui.moveTo(x_aba, y_aba, duration=0.5)
        pyautogui.click()
        time.sleep(5)  # Aumentado o delay para garantir carregamento da aba

        if verificar_energia() and clicar_no_botao(button_claim_template, f"Botão CLAIM encontrado na aba {i+1}"):
            processar_aba(x_janela, y_janela)  # Se encontrar, processa imediatamente
            return True  

    return False  # Não encontrou nenhum botão Claim em nenhuma aba

def processar_aba(x_janela, y_janela):
    """Executa a sequência de cliques para uma aba."""
    print("Procurando botão CLAIM...")

    if not verificar_energia():
        return  # Se não houver energia, não tenta clicar no Claim

    if not clicar_no_botao(button_claim_template, "Botão CLAIM"):
        print("Botão CLAIM não encontrado. Verificando se é necessário clicar no botão PLAY...")
        
        if clicar_no_botao(button_play_template, "Botão PLAY"):
            print("Botão PLAY clicado. Esperando 10 segundos para carregar...")
            time.sleep(10)
            
            if verificar_todas_abas(x_janela, y_janela):
                return processar_aba(x_janela, y_janela)

        print("Nenhum botão Claim encontrado. Temporizador ativado. Aguardando o próximo ciclo...")
        return

    time.sleep(1)

    print("Procurando botão OK...")
    
    while not clicar_no_botao(button_ok_template, "Botão OK"):
        time.sleep(2)
    
    time.sleep(7)

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

        print(f"Alternando para a aba {i + 1}...")
        pyautogui.moveTo(x_aba, y_aba, duration=0.5)
        pyautogui.click()
        time.sleep(6)  # Aumentado o tempo de espera após trocar de aba

        processar_aba(x_janela, y_janela)

    print(f"Aguardando {horas} horas e {minutos} minutos antes de repetir o processo...")
    time.sleep(tempo_de_espera)
