import time
import os
import pyautogui
import cv2
import numpy as np
import pygetwindow as gw
import mss
import mss.tools
import sys

# Redireciona a saída de erro para um arquivo log.txt
sys.stderr = open("error_log.txt", "w")

# Captura erros inesperados e salva no arquivo
def excecao_tratada(exctype, value, traceback):
    with open("error_log.txt", "a") as f:
        f.write(f"\n[ERRO] {exctype.__name__}: {value}\n")
    print(f"Erro detectado: {value}. Veja o arquivo error_log.txt para mais detalhes.")

sys.excepthook = excecao_tratada


# Tela de apresentação
def mostrar_tela_apresentacao():
    os.system("cls" if os.name == "nt" else "clear")  # Limpa a tela
    banner = """
████████╗ ██████╗ ███╗   ██╗    ██╗    ██╗ █████╗ ██████╗ ███████╗██████╗ 
╚══██╔══╝██╔═══██╗████╗  ██║    ██║    ██║██╔══██╗██╔══██╗██╔════╝██╔══██╗
   ██║   ██║   ██║██╔██╗ ██║    ██║ █╗ ██║███████║██████╔╝█████╗  ██████╔╝
   ██║   ██║   ██║██║╚██╗██║    ██║███╗██║██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗
   ██║   ╚██████╔╝██║ ╚████║    ╚███╔███╔╝██║  ██║██║     ███████╗██║  ██║
   ╚═╝    ╚═════╝ ╚═╝  ╚═══╝     ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝
    """
    print(banner)
    print("🔥 Ton Warrior Bot - Automação para Telegram 🔥")
    print("🚀 Desenvolvido por Seensh")
    print("🔧 Aguarde, preparando o ambiente...\n")
    time.sleep(3)

# Chama a tela de apresentação antes de começar
mostrar_tela_apresentacao()

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

# Função para encontrar o caminho correto dos arquivos dentro do executável
def resource_path(relative_path):
    """ Retorna o caminho absoluto do recurso, lidando com o PyInstaller. """
    if hasattr(sys, '_MEIPASS'):  # Se rodando como executável
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Carrega as imagens dos botões
button_claim_template = cv2.imread('assets/claim.png', cv2.IMREAD_UNCHANGED)
button_ok_template = cv2.imread('assets/ok.png', cv2.IMREAD_UNCHANGED)
button_start_template = cv2.imread('assets/start.png', cv2.IMREAD_UNCHANGED)
button_play_template = cv2.imread('assets/play.png', cv2.IMREAD_UNCHANGED)
power_zero_template = cv2.imread('assets/0percent.png', cv2.IMREAD_UNCHANGED)
button_backpack_template = cv2.imread('assets/backpack.png', cv2.IMREAD_UNCHANGED)
button_inicio_play_template = cv2.imread('assets/inicioPlay.png', cv2.IMREAD_UNCHANGED)

# Coordenadas RELATIVAS das abas dentro da janela do jogo
abas_relativas = [
    (55, 543),  # Aba 1
    (114, 540),  # Aba 2
    (177, 541),  # Aba 3
    (243, 541),  # Aba 4
    (301, 543),  # Aba 5
    (361, 540)   # Aba 6
]

# Coordenadas das abas dentro da Backpack
backpack_abas_relativas = [
    (88, 260),   # Aba 1
    (125, 260),  # Aba 2
    (156, 258),  # Aba 3
    (202, 257),  # Aba 4
    (241, 258),  # Aba 5
    (281, 258),  # Aba 6
    (320, 259)   # Aba 7
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
    locais = encontrar_botao(power_zero_template, limiar=0.9)
    if locais:
        print("⚡ [SEM ENERGIA] 0% detectado! Abrindo Backpack para limpar itens...")
        abrir_backpack()
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

def abrir_backpack():
    """Clica no botão Backpack e remove a seleção das 7 abas."""
    if clicar_no_botao(button_backpack_template, "Botão BACKPACK"):
        print("🎒 Backpack aberto! Limpando abas...")
        time.sleep(2)

        for i, (x_rel, y_rel) in enumerate(backpack_abas_relativas):
            x_aba = x_janela + x_rel
            y_aba = y_janela + y_rel
            
            pyautogui.moveTo(x_aba, y_aba, duration=0.5)
            pyautogui.click()
            print(f"✔ Aba {i+1} do Backpack desmarcada.")
            time.sleep(2)
        
        print("🔄 Voltando ao jogo...")
        if clicar_no_botao(button_inicio_play_template, "Botão INICIO PLAY"):
            print("🎮 Jogo retomado! Continuando a verificação das abas...")
            time.sleep(5)  # Aguarda um tempo para garantir o carregamento do jogo

def verificar_tempo_proximo():
    """Verifica se a verificação de 2 horas está próxima da execução normal do bot."""
    tempo_restante = (ultimo_teste + tempo_verificacao) - time.time()
    
    if tempo_restante < 600:  # Menos de 10 minutos para o ciclo normal
        print("⏳ Verificação extra está muito próxima do ciclo normal. Pulando esta verificação...")
        return False
    return True


def verificar_todas_abas(x_janela, y_janela):
    """Verifica todas as abas para ver se há um botão Claim disponível e inicia o ciclo se encontrar."""
    for i, (x_rel, y_rel) in enumerate(abas_relativas):
        x_aba = x_janela + x_rel
        y_aba = y_janela + y_rel

        pyautogui.moveTo(x_aba, y_aba, duration=0.5)
        pyautogui.click()
        time.sleep(5)

        if clicar_no_botao(button_claim_template, f"Botão CLAIM encontrado na aba {i+1}"):
            processar_aba(x_janela, y_janela)
            return True  

    return False  

def processar_aba(x_janela, y_janela):
    """Executa a sequência de cliques para uma aba."""
    print("Procurando botão CLAIM...")

    if not verificar_energia():
        return  

    while not clicar_no_botao(button_claim_template, "Botão CLAIM"):
        print("Botão CLAIM não encontrado. Verificando se é necessário clicar no botão PLAY...")
        
        if clicar_no_botao(button_play_template, "Botão PLAY"):
            print("Botão PLAY clicado. Esperando 10 segundos para carregar...")
            time.sleep(10)
            continue  

        print("Nenhum botão Claim encontrado. Pulando esta aba.")
        return

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
        time.sleep(8)

        processar_aba(x_janela, y_janela)

    print(f"Aguardando {horas} horas e {minutos} minutos antes de repetir o processo...")

    while time.time() - ultimo_teste < tempo_verificacao:
        time.sleep(300)

        if time.time() - ultimo_teste >= tempo_verificacao:
            if verificar_tempo_proximo():  # Impede execução se estiver perto do ciclo normal
                print("🔄 [VERIFICAÇÃO] Checando todas as abas para ver se há um botão CLAIM disponível...")
                if verificar_todas_abas(x_janela, y_janela):
                    ultimo_teste = time.time()