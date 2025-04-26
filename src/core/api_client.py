"""Cliente para API de resultados"""
import requests
import json
import logging

logger = logging.getLogger(__name__)

from typing import List

class APIClient:
    """Cliente para API de resultados do Bac Bo"""
    
    def __init__(self, url: str):
        self.url = url

    def obter_resultados(self) -> List[str]:
        """Obtém resultados da API"""
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
        """Parseia os resultados da API"""
        try:
            json_data = json.loads(response_text)
            return [i for i in json_data if i in ('A', 'V', 'E')]
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            return []