import pyautogui
import pygetwindow as gw
import time

def capturar_coordenadas(qtd_posicoes=7):
    """Captura múltiplas posições do mouse e exibe as coordenadas absolutas e relativas à janela do Telegram."""
    try:
        # Obtém a posição e tamanho da janela do Telegram
        janela = gw.getWindowsWithTitle("Miniapp: Ton Warrior bot")[0]
        x_janela, y_janela, largura, altura = janela.left, janela.top, janela.width, janela.height

        coordenadas = []

        for i in range(1, qtd_posicoes + 1):
            print(f"\n🚀 Posicione o mouse sobre o local {i} dentro do Telegram.")
            print("Aguarde 3 segundos...\n")
            time.sleep(3)  # Tempo para posicionar o mouse

            # Captura coordenadas
            x_abs, y_abs = pyautogui.position()  # Coordenadas absolutas
            x_rel, y_rel = x_abs - x_janela, y_abs - y_janela  # Coordenadas relativas à janela

            coordenadas.append((x_abs, y_abs, x_rel, y_rel))

            print(f"📍 Posição {i} - Coordenadas Absolutas: X={x_abs}, Y={y_abs}")
            print(f"📌 Posição {i} - Coordenadas Relativas à Janela: X={x_rel}, Y={y_rel}")

        # Exibir todas as coordenadas ao final
        print("\n📌 Coordenadas Capturadas:")
        for i, (x_abs, y_abs, x_rel, y_rel) in enumerate(coordenadas, start=1):
            print(f"🔹 Posição {i}: Absolutas (X={x_abs}, Y={y_abs}) | Relativas à Janela (X={x_rel}, Y={y_rel})")

    except IndexError:
        print("❌ Janela do Telegram não encontrada! Certifique-se de que ela está aberta.")

# Chamada da função
capturar_coordenadas()
