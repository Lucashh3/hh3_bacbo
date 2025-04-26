"""Módulo principal do bot de sinais para cassino."""

import datetime
import json
import time
import logging
from typing import List, Dict, Optional, Tuple
import requests
import telebot
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

class ConfiguracaoBot:
    """Classe para armazenar as configurações do bot."""
    
    def __init__(self):
        """Inicializa as configurações padrão."""
        self.game = "Entrar no BAC BO"
        self.token = '6957899527:AAHCmWhTV5WZkalec4A2J4w6YqTPhzDi_MI'
        self.chat_id = '-4642070993'
        self.url_api = 'http://rodrigodevapi.duckdns.org:1010/bacbo-live'
        self.gales = 2
        self.protection = True
        self.link = '[Clique aqui!](https://www.seu.bet.br/slots/all/28/evolution/34940-420012128-bac-bo?btag=2313822&accounts=%2A&login=%2A&mode=real)'

class Resultados:
    """Classe para gerenciar os resultados das apostas."""
    
    def __init__(self):
        """Inicializa os contadores de resultados."""
        self.win = 0
        self.empate = 0
        self.loss = 0
        self.max_consecutivas = 0
        self.assertividade = "0%"

class TelegramBotHandler:
    """Classe para manipular interações com o Telegram."""
    
    def __init__(self, token: str, chat_id: str):
        """Inicializa o bot do Telegram."""
        self.bot = telebot.TeleBot(token=token, parse_mode='MARKDOWN')
        self.chat_id = chat_id
        self.message_delete = False
        self.message_id: Optional[int] = None

    def enviar_mensagem(self, texto: str) -> None:
        """Envia mensagem para o chat."""
        try:
            self.bot.send_message(chat_id=self.chat_id, text=texto)
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")

    def enviar_alerta(self, estrategia_nome: str = "") -> None:
        """Envia mensagem de alerta com o nome da estratégia."""
        msg = "⚠️ ANALISANDO, FIQUE ATENTO!!!"
        if estrategia_nome:
            msg += f"\n🔍 Estratégia: {estrategia_nome}"
        
        try:
            self.message_id = self.bot.send_message(
                self.chat_id, 
                text=msg
            ).message_id
            self.message_delete = True
        except Exception as e:
            logger.error(f"Erro ao enviar alerta: {e}")

    def enviar_gale(self, numero_gale: int) -> None:
        """Envia mensagem de gale."""
        msg = f"⚠️ Vamos para o {numero_gale}ª GALE"
        try:
            self.message_id = self.bot.send_message(
                self.chat_id, 
                text=msg
            ).message_id
            self.message_delete = True
        except Exception as e:
            logger.error(f"Erro ao enviar gale: {e}")

    def enviar_sinal(self, direcao: str, gales: int, game: str, link: str, estrategia_nome: str = "") -> None:
        """Envia sinal confirmado com nome da estratégia."""
        msg = f"""
🎲 *ENTRADA CONFIRMADA!* {'(' + estrategia_nome + ')' if estrategia_nome else ''}

🎰 Apostar no {direcao}
🟡 Proteger o empate 
🔁 Fazer até {gales} gales

📱 *{game}* {link}
        """
        try:
            self.bot.send_message(chat_id=self.chat_id, text=msg)
        except Exception as e:
            logger.error(f"Erro ao enviar sinal: {e}")

    def deletar_ultima_mensagem(self) -> None:
        """Deleta a última mensagem enviada."""
        if self.message_delete and self.message_id:
            try:
                self.bot.delete_message(
                    chat_id=self.chat_id,
                    message_id=self.message_id
                )
                self.message_delete = False
            except Exception as e:
                logger.error(f"Erro ao deletar mensagem: {e}")

class APIClient:
    """Classe para interação com a API de resultados."""
    
    def __init__(self, url: str):
        """Inicializa o cliente da API."""
        self.url = url

    def obter_resultados(self) -> List[str]:
        """Obtém os resultados mais recentes da API."""
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
        """Parseia os resultados da API."""
        try:
            json_data = json.loads(response_text)
            return [i for i in json_data if i in ('A', 'V', 'E')]
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            return []

class EstrategiaManager:
    """Classe para gerenciar as estratégias de aposta."""
    
    def __init__(self, arquivo_estrategias: str = 'estrategy.csv'):
        """Inicializa o gerenciador de estratégias."""
        self.arquivo = arquivo_estrategias
        self.estrategias = self._carregar_estrategias()

    def _carregar_estrategias(self) -> List[Dict]:
        """Carrega as estratégias do arquivo CSV."""
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
        """Encontra estratégias que correspondam aos resultados."""
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

class BotCassino:
    """Classe principal do bot de cassino."""
    
    def __init__(self):
        """Inicializa o bot com todas as dependências."""
        self.config = ConfiguracaoBot()
        self.resultados = Resultados()
        self.telegram = TelegramBotHandler(self.config.token, self.config.chat_id)
        self.api = APIClient(self.config.url_api)
        self.estrategias = EstrategiaManager()
        
        self.analisando = True
        self.direcao = 'None'
        self.count_gales = 0
        self.data_atual = self._obter_data_atual()

    def _obter_data_atual(self) -> str:
        """Retorna a data atual formatada."""
        return datetime.datetime.now().strftime("%d/%m/%Y")

    def reiniciar_diario(self) -> bool:
        """Reinicia os contadores diários."""
        nova_data = self._obter_data_atual()
        if nova_data != self.data_atual:
            logger.info("Reiniciando contadores diários")
            self.data_atual = nova_data
            self.resultados = Resultados()
            return True
        return False

    def calcular_assertividade(self) -> str:
        """Calcula a porcentagem de acertos."""
        total = self.resultados.win + self.resultados.empate + self.resultados.loss
        if total == 0:
            return "0%"
        acertos = self.resultados.win + self.resultados.empate
        return f"{(100 * acertos / total):.2f}%"

    def enviar_placar(self) -> None:
        """Envia o placar atual para o Telegram."""
        placar = f"""
► PLACAR GERAL = ✅{self.resultados.win} | 🟡{self.resultados.empate} | 🚫{self.resultados.loss} 
► Consecutivas = {self.resultados.max_consecutivas}
► Assertividade = {self.calcular_assertividade()}
        """
        self.telegram.enviar_mensagem(placar)

    def processar_resultado(self, resultado: str) -> None:
        """Processa o resultado de uma aposta."""
        try:
            if resultado == "WIN":
                logger.info("Resultado: WIN")
                self.resultados.win += 1
                self.resultados.max_consecutivas += 1
                self.telegram.enviar_mensagem("✅✅✅ WIN ✅✅✅")
                
            elif resultado == "EMPATE":
                logger.info("Resultado: EMPATE")
                self.resultados.empate += 1
                self.resultados.max_consecutivas += 1
                self.telegram.enviar_mensagem("✅✅✅ EMPATE ✅✅✅")
                
            elif resultado == "LOSS":
                self.count_gales += 1
                
                if self.count_gales > self.config.gales:
                    logger.info("Resultado: LOSS")
                    self.resultados.loss += 1
                    self.resultados.max_consecutivas = 0
                    self.telegram.enviar_mensagem("🚫🚫🚫 LOSS - ESPERE SEQUÊNCIA DE 3 GREENS 🚫🚫🚫")
                else:
                    logger.info(f"Vamos para o {self.count_gales}ª gale")
                    self.telegram.enviar_gale(self.count_gales)
                    return
            
            # Resetar após processamento
            self.count_gales = 0
            self.analisando = True
            self.enviar_placar()
            self.reiniciar_diario()
            
        except Exception as e:
            logger.error(f"Erro ao processar resultado: {e}")

    def analisar_resultados(self, resultados: List[str]) -> None:
        """Analisa os resultados e toma decisões de aposta."""
        try:
            if not self.analisando:
                self.verificar_resultado(resultados[0])
                return
                
            estrategia, estrategia_parcial = self.estrategias.encontrar_estrategia(resultados)
            
            if estrategia:
                logger.info(f"Estratégia encontrada: {estrategia['nome']}")
                self.direcao = self._mapear_direcao(estrategia['entrada'])
                self.analisando = False
                self.telegram.enviar_sinal(
                    self.direcao,
                    self.config.gales,
                    self.config.game,
                    self.config.link,
                    estrategia['nome']
                )
            elif estrategia_parcial:
                logger.info(f"Padrão parcial encontrado para estratégia: {estrategia_parcial['nome']}")
                self.telegram.enviar_alerta(estrategia_parcial['nome'])
                        
        except Exception as e:
            logger.error(f"Erro ao analisar resultados: {e}")

    def _mapear_direcao(self, entrada: str) -> str:
        """Mapeia a entrada para o emoji correspondente."""
        if entrada == "A":
            return "🔵"
        elif entrada == "V":
            return "🔴"
        elif entrada == "E":
            return "🟡"
        return "None"

    def verificar_resultado(self, resultado: str) -> None:
        """Verifica o resultado contra a direção apostada."""
        try:
            if resultado == 'V' and self.direcao == '🔴':
                self.processar_resultado("WIN")
            elif resultado == 'V' and self.direcao == '🔵':
                self.processar_resultado("LOSS")
            elif resultado == 'A' and self.direcao == '🔵':
                self.processar_resultado("WIN")
            elif resultado == 'A' and self.direcao == '🔴':
                self.processar_resultado("LOSS")
            elif resultado == 'E' and self.config.protection:
                self.processar_resultado("EMPATE")
            elif resultado == 'E' and not self.config.protection:
                self.processar_resultado("LOSS")
        except Exception as e:
            logger.error(f"Erro ao verificar resultado: {e}")

    def executar(self) -> None:
        """Método principal para execução do bot."""
        logger.info("Iniciando bot...")
        resultados_anteriores = []
        
        while True:
            try:
                self.reiniciar_diario()
                
                resultados = self.api.obter_resultados()
                if not resultados:
                    time.sleep(1)
                    continue
                    
                if resultados != resultados_anteriores:
                    logger.debug(f"Novos resultados: {resultados}")
                    resultados_anteriores = resultados
                    self.telegram.deletar_ultima_mensagem()
                    self.analisar_resultados(resultados)
                    
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Erro inesperado: {e}")
                time.sleep(5)

if __name__ == "__main__":
    try:
        logger.info("Inicializando BotCassino")
        bot = BotCassino()
        bot.executar()
    except KeyboardInterrupt:
        logger.info("Bot encerrado pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")