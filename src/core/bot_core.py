"""Módulo principal do bot Bac Bo"""
import time
import random
import logging
import pyautogui
from typing import List, Dict, Optional
from src.config.config_manager import ConfigManager
from src.core.estrategias import EstrategiaManager
from src.core.api_client import APIClient
from src.config.coordenadas import CoordenadasManager

logger = logging.getLogger(__name__)

class BotCassino:
    """Classe principal do bot com automação pyautogui"""
    
    def __init__(self):
        config_manager = ConfigManager()
        self.config = config_manager.config
        self.estrategias = EstrategiaManager()
        self.coordenadas = CoordenadasManager().coordenadas
        self.api = APIClient("http://rodrigodevapi.duckdns.org:1010/bacbo-live")
        
        self.analisando = True
        self.direcao = 'None'
        self.count_gales = 0
        self.ultima_aposta = None
        self.consec_losses = 0
        self.max_gales = self.config['max_gales']
        self.stop_loss = self.config['stop_loss']
        self.valor_base = self.config['aposta_base']
        
        # Contadores
        self.win = 0
        self.empate = 0
        self.loss = 0
        self.max_consecutivas = 0

    def executar(self):
        """Loop principal do bot"""
        logger.info("Iniciando bot...")
        resultados_anteriores = []
        
        while True:
            try:
                resultados = self.api.obter_resultados()
                if not resultados:
                    time.sleep(1)
                    continue
                    
                if resultados != resultados_anteriores:
                    logger.debug(f"Novos resultados: {resultados}")
                    resultados_anteriores = resultados.copy()
                    self._processar_resultados(resultados)
                    
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Erro inesperado: {e}")
                time.sleep(5)

    def _processar_resultados(self, resultados: List[str]):
        """Processa novos resultados"""
        if not self.analisando:
            # Verifica todos os resultados recentes para empates
            for resultado in resultados:
                if resultado in ['A', 'V', 'E']:
                    self._verificar_resultado(resultado)
                    break  # Processa apenas o primeiro resultado válido
            return
            
        estrategia = self.estrategias.encontrar_estrategia(resultados)
        if estrategia and estrategia['entrada'] in ['A', 'V', 'E']:
            self._executar_estrategia(estrategia)
        elif 'E' in resultados:
            # Forçar verificação de empate mesmo sem estratégia
            self._verificar_resultado('E')

    def _mapear_direcao(self, entrada: str) -> str:
        """Mapeia a entrada da estratégia para direção de aposta"""
        mapeamento = {
            'A': 'Azul',
            'V': 'Vermelho',
            'E': 'Empate'
        }
        return mapeamento.get(entrada, 'None')

    def _calcular_valor_gale(self):
        """Calcula o valor da aposta considerando gales"""
        if self.count_gales == 0:
            return self.valor_base
            
        try:
            if self.count_gales <= len(self.config['gale_multiplicadores']):
                multiplicador = self.config['gale_multiplicadores'][self.count_gales - 1]
            else:
                multiplicador = self.config['gale_multiplicadores'][-1]
            return int(self.valor_base * multiplicador)
        except (KeyError, IndexError) as e:
            logger.error(f"Erro ao calcular gale: {e}")
            return self.valor_base

    def _fazer_aposta(self, direcao: str):
        """Executa a aposta usando pyautogui com múltiplas fichas"""
        valor_total = self._calcular_valor_gale()
        fichas_disponiveis = [25, 10, 5]
        valor_restante = valor_total
        
        try:
            # Ordena do maior para o menor valor
            for ficha in sorted(fichas_disponiveis, reverse=True):
                while valor_restante >= ficha:
                    pyautogui.click(self.coordenadas[f'ficha_{ficha}'])
                    valor_restante -= ficha
                    time.sleep(0.2)  # Pequeno delay entre cliques
            
            if valor_restante > 0:
                logger.warning(f"Não foi possível apostar valor exato {valor_total}. Apostado: {valor_total - valor_restante}")

            # Mapeia direção para nome de coordenada
            direcao_coord = {
                'a': 'azul',
                'v': 'vermelho',
                'e': 'empate'
            }.get(direcao.lower(), direcao.lower())
            
            if direcao_coord not in self.coordenadas:
                raise ValueError(f"Direção {direcao} inválida. Use 'a', 'v' ou 'e'")
                
            # Clica na direção da aposta
            pyautogui.click(self.coordenadas[direcao_coord])
            time.sleep(0.5)
            
            # Confirma a aposta
            pyautogui.click(self.coordenadas['confirmar'])
            
            logger.info(f"Aposta de R${valor_total - valor_restante} realizada em {direcao}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao fazer aposta: {e}")
            return False
        try:
            # Mapear direção para coordenadas
            coord = {
                'A': self.coordenadas['azul'],
                'V': self.coordenadas['vermelho'],
                'E': self.coordenadas['empate']
            }.get(direcao)
            
            if not coord:
                raise ValueError(f"Direção inválida: {direcao}")
                
            # Usa a função centralizada de cálculo de gales
            valor_aposta = self._calcular_valor_gale()
            ficha = f'ficha_{valor_aposta}'
            
            if ficha not in self.coordenadas:
                logger.error(f"Ficha de valor {valor_aposta} não configurada")
                raise ValueError("Valor de aposta inválido")
                
            # Clicar na ficha
            pyautogui.click(
                x=self.coordenadas[ficha][0],
                y=self.coordenadas[ficha][1],
                duration=0.5
            )
            
            # Clicar na área de aposta
            pyautogui.click(
                x=coord[0],
                y=coord[1],
                duration=0.7
            )
            
            # Confirmar aposta
            pyautogui.click(
                x=self.coordenadas['confirmar'][0],
                y=self.coordenadas['confirmar'][1],
                duration=0.3
            )
            
            logger.info(f"Aposta realizada em {direcao}")
            
        except Exception as e:
            logger.error(f"Erro ao fazer aposta: {e}")
            raise

    def _verificar_resultado(self, resultado: str):
        """Verifica o resultado da última aposta"""
        try:
            if not self.ultima_aposta:
                return
                
            if resultado == self.ultima_aposta:
                self.win += 1
                self.consec_losses = 0
                self.count_gales = 0
                logger.info("Aposta vencedora!")
                self.ultima_aposta = None
                self.analisando = True  # Retornar ao modo de análise após vitória
            elif resultado == 'E':
                self.win += 1  # Empate conta como vitória
                self.consec_losses = 0
                self.count_gales = 0
                logger.info("Empate - contado como vitória!")
                self.analisando = True
                self.ultima_aposta = None
            else:
                if self.count_gales < self.max_gales:
                    self.count_gales += 1
                    logger.info(f"Perda - aplicando gale {self.count_gales}/{self.max_gales}")
                    logger.info(f"Aguardando 3 segundos antes do gale {self.count_gales}...")
                    time.sleep(3)
                    self.analisando = False
                    self.direcao = self._mapear_direcao(self.ultima_aposta)
                    # Forçar nova aposta imediatamente no gale
                    self._fazer_aposta(self.ultima_aposta)
                    
                    # Não zera ultima_aposta para manter referência nos gales
                else:
                    self.loss += 1
                    self.consec_losses += 1
                    self.count_gales = 0
                    logger.info("Aposta perdida - máximo de gales atingido")
                    self.ultima_aposta = None
                    self.analisando = True  # Retornar ao modo de análise
                    
                    if self.consec_losses >= self.stop_loss:
                        logger.warning(f"Stop loss atingido! {self.consec_losses} perdas consecutivas")
                        self._pausar_operacoes()
                    else:
                        logger.info("Reiniciando ciclo de apostas")
            
        except Exception as e:
            logger.error(f"Erro ao verificar resultado: {e}")
            raise

    def _pausar_operacoes(self):
        """Pausa as operações após stop loss"""
        try:
            logger.warning("Pausando operações por 30 minutos...")
            time.sleep(1800)  # 30 minutos
            self.consec_losses = 0
            logger.info("Retomando operações")
        except Exception as e:
            logger.error(f"Erro ao pausar operações: {e}")
            raise

    def _executar_estrategia(self, estrategia: Dict):
        """Executa uma estratégia válida"""
        logger.info(f"Estratégia encontrada: {estrategia['nome']}")
        self.direcao = self._mapear_direcao(estrategia['entrada'])
        self.analisando = False
        
        wait_time = random.uniform(5, 8)
        logger.info(f"Aguardando {wait_time:.1f} segundos antes de apostar...")
        time.sleep(wait_time)
        
        if self.direcao != 'None' and not self.analisando:
            logger.info(f"Fazendo aposta em: {estrategia['entrada']}")
            self._fazer_aposta(estrategia['entrada'])
            self.ultima_aposta = estrategia['entrada']