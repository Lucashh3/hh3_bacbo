"""Script para capturar coordenadas do mouse para o Bac Bo"""

import pyautogui
import json
import time

# Configurações
ARQUIVO_COORDENADAS = 'coordenadas_bacbo.json'
pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = True

def main():
    print("=== Capturador de Coordenadas para Bac Bo ===")
    print("Instruções:")
    print("1. Posicione o mouse no elemento desejado")
    print("2. Digite o nome da coordenada (ex: azul, ficha_5)")
    print("3. Pressione Enter para salvar")
    print("4. Digite 'sair' para finalizar\n")

    try:
        # Carrega coordenadas existentes
        with open(ARQUIVO_COORDENADAS, 'r') as f:
            coordenadas = json.load(f)
    except:
        coordenadas = {
            'azul': [0, 0],
            'vermelho': [0, 0],
            'empate': [0, 0],
            'ficha_5': [0, 0],
            'ficha_10': [0, 0],
            'ficha_25': [0, 0],
            'confirmar': [0, 0]
        }

    while True:
        # Mostra posição atual
        x, y = pyautogui.position()
        print(f"\nPosição atual: X={x} Y={y}")
        print("Coordenadas salvas:")
        for nome, coord in coordenadas.items():
            print(f"- {nome}: {coord}")

        # Captura input
        nome = input("\nNome da coordenada (ou 'sair'): ").strip().lower()
        
        if nome == 'sair':
            break
            
        if nome in coordenadas:
            # Atualiza coordenada
            coordenadas[nome] = [x, y]
            
            # Salva no arquivo
            with open(ARQUIVO_COORDENADAS, 'w') as f:
                json.dump(coordenadas, f, indent=2)
                
            print(f"Coordenada '{nome}' salva: [{x}, {y}]")
        else:
            print("Nome inválido. Use: azul, vermelho, empate, ficha_5, ficha_10, ficha_25, confirmar")

if __name__ == "__main__":
    main()