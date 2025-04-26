"""Gerenciador de configurações do bot"""
import json
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """Gerencia as configurações do bot"""
    
    DEFAULT_CONFIG = {
        'aposta_base': 20,
        'aposta_empate': 5,
        'gale_multiplicadores': [2.0, 3.5],
        'max_gales': 2,
        'stop_loss': 3,
        'saldo_inicial': 1000,
        'protection': True
    }

    def __init__(self):
        self.config = self.DEFAULT_CONFIG.copy()
        self._carregar_config()

    def _carregar_config(self):
        """Carrega configurações do arquivo JSON"""
        try:
            with open('src/config/config_apostas.json', 'r') as f:
                self.config.update(json.load(f))
            logger.info("Configurações carregadas com sucesso")
        except FileNotFoundError:
            logger.warning("Arquivo de configuração não encontrado - usando padrões")
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")