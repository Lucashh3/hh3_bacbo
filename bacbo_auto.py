"""Bot automatizado para Bac Bo baseado no bot_refatorado.py com automação pyautogui"""

import pyautogui
import time
import random
import datetime
import json
import logging
from typing import List, Dict, Optional, Tuple
import requests
import csv

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configurações padrão do bot
pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = False  # ATENÇÃO: Desativado por solicitação

class ConfigManager:
    """Gerenciador de configurações com suporte a pyautogui"""
    
    def __init__(self):
        self.config = {
            'aposta_base': 20,
            'aposta_empate': 5,
            'gale_multiplicadores': [2.0, 3.5],
            'max_gales': 2,
            'stop_loss': 3,
            'saldo_inicial': 1000,
            'protection': True,
            'coordenadas': {}
        }
        self.carregar_config()

    def carregar_config(self):
        """Carrega configurações do arquivo JSON"""
        try:
            with open('config_apostas.json', 'r') as f:
                self.config.update(json.load(f))
            logger.info("Configurações carregadas com sucesso")
        except FileNotFoundError:
            logger.warning("Arquivo de configuração não encontrado - usando padrões")
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")

class BotCassino:
    """Classe principal do bot com automação pyautogui"""
    
    def __init__(self):
        self.config = ConfigManager().config
        self.estrategias = EstrategiaManager()
        
        try:
            with open('coordenadas_bacbo.json', 'r') as f:
                self.coordenadas = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError("Arquivo coordenadas_bacbo.json não encontrado")
        except json.JSONDecodeError:
            raise ValueError("Arquivo coordenadas_bacbo.json inválido")
                
        # Valida coordenadas obrigatórias
        required_coords = ['azul', 'vermelho', 'empate', 'ficha_5']
        for coord in required_coords:
            if coord not in self.coordenadas:
                raise ValueError(f"Coordenada obrigatória faltando: {coord}")
            if not isinstance(self.coordenadas[coord], list) or len(self.coordenadas[coord]) != 2:
                raise ValueError(f"Coordenada {coord} inválida. Deve ser uma lista [x,y]")
            if self.coordenadas[coord] == [0, 0]:
                raise ValueError(f"Coordenada {coord} não configurada. Execute capturar_coordenadas.py")
                    
        logger.info("Configurações e coordenadas carregadas com sucesso")
        
        self.analisando = True
        self.direcao = 'None'
        self.count_gales = 0
        self.data_atual = self._obter_data_atual()
        
        # Contadores de resultados
        self.win = 0
        self.empate = 0
        self.loss = 0
        self.max_consecutivas = 0

    def _obter_data_atual(self) -> str:
        return datetime.datetime.now().strftime("%d/%m/%Y")

    def reiniciar_diario(self) -> bool:
        nova_data = self._obter_data_atual()
        if nova_data != self.data_atual:
            logger.info("Reiniciando contadores diários")
            self.data_atual = nova_data
            self.win = 0
            self.empate = 0
            self.loss = 0
            self.max_consecutivas = 0
            return True
        return False

    def fazer_aposta(self, cor: str) -> bool:
        """Adaptação para pyautogui da lógica de aposta"""
        try:
            cor = cor.upper()
            if cor not in ['A', 'V', 'E']:
                raise ValueError(f"Cor inválida: {cor}. Use A (azul), V (vermelho) ou E (empate)")
                
            # Mapeamento direto das cores
            coord_name = {
                'A': 'azul',    # A = Azul
                'V': 'vermelho', # V = Vermelho
                'E': 'empate'    # E = Empate
            }[cor]
            if coord_name not in self.coordenadas or self.coordenadas[coord_name] == [0, 0]:
                raise ValueError(f"Coordenada para {coord_name} não configurada. Execute capturar_coordenadas.py")

            # Calcula valor baseado no gale atual
            if self.count_gales == 0:
                valor_cor = self.config['aposta_base']
                valor_empate = self.config['aposta_empate']
            else:
                gale_index = min(self.count_gales - 1, len(self.config['gale_multiplicadores']) - 1)
                mult = self.config['gale_multiplicadores'][gale_index]
                valor_cor = max(5, round(self.config['aposta_base'] * mult))
                valor_empate = max(5, round(self.config['aposta_empate'] * mult))
                
            logger.debug(f"Gale {self.count_gales} - Valor Cor: {valor_cor} | Valor Empate: {valor_empate}")

            try:
                # Seleciona ficha adequada para aposta principal
                self._selecionar_ficha(valor_cor)
                
                # Faz aposta principal
                pyautogui.click(*self.coordenadas[coord_name])
                time.sleep(0.5)
                logger.debug(f"Aposta em {coord_name} com valor {valor_cor}")
                
                # Faz proteção de empate se configurado
                if self.config['protection'] and valor_empate > 0:
                    self._selecionar_ficha(valor_empate)
                    pyautogui.click(*self.coordenadas['empate'])
                    time.sleep(0.5)
                    logger.debug(f"Proteção de empate com valor {valor_empate}")
                    
                logger.info(f"Aposta realizada: {cor} - Valor: {valor_cor} | Empate: {valor_empate}")
                return True
                    
            except Exception as e:
                logger.error(f"Erro ao fazer aposta: {e}")
                return False

        except Exception as e:
            logger.error(f"Erro geral ao processar aposta: {e}")
            return False

    def _selecionar_ficha(self, valor: int) -> None:
        """Seleciona a ficha adequada baseada no valor"""
        try:
            if valor >= 25 and 'ficha_25' in self.coordenadas:
                pyautogui.click(*self.coordenadas['ficha_25'])
            elif valor >= 10 and 'ficha_10' in self.coordenadas:
                pyautogui.click(*self.coordenadas['ficha_10'])
            else:
                pyautogui.click(*self.coordenadas['ficha_5'])
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"Erro ao selecionar ficha: {e}")
            raise

    def analisar_resultados(self, resultados: List[str]) -> None:
        """Método idêntico ao do bot_refatorado"""
        try:
            if not self.analisando:
                if resultados and resultados[0] in ['A', 'V', 'E']:
                    self.verificar_resultado(resultados[0])
                return
                
            estrategia, estrategia_parcial = self.estrategias.encontrar_estrategia(resultados)
            
            if estrategia and estrategia['entrada'] in ['A', 'V', 'E']:
                logger.info(f"Estratégia válida encontrada: {estrategia['nome']} - Entrada: {estrategia['entrada']}")
                self.direcao = self._mapear_direcao(estrategia['entrada'])
                self.analisando = False
                
                # Aguarda tempo aleatório entre 5-8 segundos antes de apostar
                wait_time = random.uniform(5, 8)
                logger.info(f"Aguardando {wait_time:.1f} segundos antes de apostar...")
                time.sleep(wait_time)
                
                # Verifica novamente antes de apostar
                if self.direcao != 'None' and not self.analisando:
                    logger.info(f"Fazendo aposta em: {estrategia['entrada']}")
                    success = self.fazer_aposta(estrategia['entrada'])
                    if not success:
                        self.analisando = True  # Reset se falhar
                else:
                    logger.warning(f"Aposta cancelada - Direção: {self.direcao}, Analisando: {self.analisando}")
                
            elif estrategia_parcial:
                logger.info(f"Padrão parcial encontrado para estratégia: {estrategia_parcial['nome']}")
                        
        except Exception as e:
            logger.error(f"Erro ao analisar resultados: {e}")

    def _mapear_direcao(self, entrada: str) -> str:
        if entrada == "A":
            return "🔵"
        elif entrada == "V":
            return "🔴"
        elif entrada == "E":
            return "🟡"
        return "None"

    def processar_resultado(self, resultado: str) -> None:
        try:
            if resultado == "WIN":
                logger.info("Resultado: WIN")
                self.win += 1
                self.max_consecutivas += 1
                
            elif resultado == "EMPATE":
                logger.info("Resultado: EMPATE")
                self.empate += 1
                self.max_consecutivas += 1
                
            elif resultado == "LOSS":
                self.count_gales += 1
                
                if self.count_gales > self.config['max_gales']:
                    logger.info("Resultado: LOSS")
                    self.loss += 1
                    self.max_consecutivas = 0
                else:
                    logger.info(f"Vamos para o {self.count_gales}ª gale")
                    return
            
            # Resetar após processamento
            self.count_gales = 0
            self.analisando = True
            self.reiniciar_diario()
            
        except Exception as e:
            logger.error(f"Erro ao processar resultado: {e}")

    def verificar_resultado(self, resultado: str) -> None:
        """Método idêntico ao do bot_refatorado"""
        try:
            # Padroniza entrada para maiúsculo
            resultado = resultado.upper()
            
            if resultado == 'V' and self.direcao == '🔵':
                self.processar_resultado("WIN")
            elif resultado == 'V' and self.direcao == '🔴':
                self.processar_resultado("LOSS")
            elif resultado == 'A' and self.direcao == '🔴':
                self.processar_resultado("WIN")
            elif resultado == 'A' and self.direcao == '🔵':
                self.processar_resultado("LOSS")
            elif resultado == 'E' and self.config['protection']:
                self.processar_resultado("EMPATE")
            elif resultado == 'E' and not self.config['protection']:
                self.processar_resultado("LOSS")
        except Exception as e:
            logger.error(f"Erro ao verificar resultado: {e}")

    def manter_ativo(self):
        """Ações para manter a sessão ativa"""
        try:
            x = random.randint(100, 500)
            y = random.randint(100, 500)
            pyautogui.moveTo(x, y, duration=0.5)
            
            if random.random() < 0.3:
                pyautogui.click()
                
            if random.random() < 0.2:
                pyautogui.scroll(random.randint(-50, 50))
                
        except Exception as e:
            logger.error(f"Erro ao executar manter_ativo: {e}")

    def executar(self) -> None:
        """Loop principal idêntico ao do bot_refatorado com adaptações para pyautogui"""
        logger.info("Iniciando bot...")
        api = APIClient("http://rodrigodevapi.duckdns.org:1010/bacbo-live")
        resultados_anteriores = []
        ultima_aposta = None
        
        while True:
            try:
                self.reiniciar_diario()
                
                resultados = api.obter_resultados()
                if not resultados:
                    time.sleep(1)
                    continue
                    
                if resultados != resultados_anteriores:
                    logger.debug(f"Novos resultados: {resultados}")
                    resultados_anteriores = resultados.copy()  # Usar copy() para evitar referência
                    
                    # Verifica se há novos resultados para analisar
                    if len(resultados) > 0 and (ultima_aposta is None or resultados[0] != ultima_aposta):
                        logger.info(f"Processando novo resultado: {resultados[0]}")
                        self.analisar_resultados(resultados)
                        ultima_aposta = resultados[0]
                    
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Erro inesperado: {e}")
                time.sleep(5)

class EstrategiaManager:
    """Classe idêntica à do bot_refatorado.py"""
    
    def __init__(self, arquivo_estrategias: str = 'estrategy.csv'):
        self.arquivo = arquivo_estrategias
        self.estrategias = self._carregar_estrategias()

    def _carregar_estrategias(self) -> List[Dict]:
        try:
            estrategias = []
            with open(self.arquivo, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and '=' in row[0]:
                        partes = row[0].split('=')
                        if len(partes) >= 2:
                            padrao = partes[0]
                            entrada = partes[1]
                            nome = partes[2] if len(partes) > 2 else f"Padrão {len(estrategias)+1}"
                            
                            estrategias.append({
                                'padrao': list(padrao)[::-1],  # Inverte a ordem
                                'entrada': entrada,
                                'nome': nome.strip()
                            })
            return estrategias
        except Exception as e:
            logger.error(f"Erro ao carregar estratégias: {e}")
            return []

    def encontrar_estrategia(self, resultados: List[str]) -> Tuple[Optional[Dict], Optional[Dict]]:
        try:
            # Procura estratégia completa
            for estrategia in self.estrategias:
                if resultados[:len(estrategia['padrao'])] == estrategia['padrao']:
                    return estrategia, None
            
            # Procura estratégia parcial para alerta
            for estrategia in self.estrategias:
                if resultados[:len(estrategia['padrao'])-1] == estrategia['padrao'][1:]:
                    return None, estrategia
                    
            return None, None
        except Exception as e:
            logger.error(f"Erro ao buscar estratégia: {e}")
            return None, None

class APIClient:
    """Classe idêntica à do bot_refatorado.py"""
    
    def __init__(self, url: str):
        self.url = url

    def obter_resultados(self) -> List[str]:
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            
            response_text = response.text.strip()
            if response_text.startswith("results:"):
                response_text = response_text[len("results:"):].strip()
                response_text = response_text.replace('\"', '"').replace("'", '"')
                
            return self._parse_resultados(response_text)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {e}")
            return []
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return []

    def _parse_resultados(self, response_text: str) -> List[str]:
        try:
            json_data = json.loads(response_text)
            return [i for i in json_data if i in ('A', 'V', 'E')]
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            return []

if __name__ == "__main__":
    try:
        logger.info("Inicializando BotCassino")
        bot = BotCassino()
        bot.executar()
    except KeyboardInterrupt:
        logger.info("Bot encerrado pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")