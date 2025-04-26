"""Gerenciador de estratégias do bot"""
import csv
import logging
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class EstrategiaManager:
    """Gerencia as estratégias de apostas"""
    
    def __init__(self, arquivo: str = 'data/estrategy.csv'):
        self.arquivo = arquivo
        self.estrategias = []
        try:
            self.estrategias = self._carregar_estrategias()
        except FileNotFoundError:
            logger.warning("Arquivo de estratégias não encontrado - usando padrões")
            self.estrategias = [
                {'padrao': ['A', 'A', 'V'], 'entrada': 'V', 'nome': 'Padrão 1'},
                {'padrao': ['V', 'V', 'A'], 'entrada': 'A', 'nome': 'Padrão 2'}
            ]

    def _carregar_estrategias(self) -> List[Dict]:
        """Carrega estratégias do arquivo CSV"""
        try:
            estrategias = []
            with open(self.arquivo, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and '=' in row[0]:
                        partes = row[0].split('=')
                        if len(partes) >= 2:
                            estrategias.append({
                                'padrao': list(partes[0])[::-1],
                                'entrada': partes[1],
                                'nome': partes[2] if len(partes) > 2 else f"Padrão {len(estrategias)+1}"
                            })
            return estrategias
        except Exception as e:
            logger.error(f"Erro ao carregar estratégias: {e}")
            return []

    def encontrar_estrategia(self, resultados: List[str]) -> Optional[Dict]:
        """Encontra estratégia correspondente aos resultados"""
        try:
            for estrategia in self.estrategias:
                if resultados[:len(estrategia['padrao'])] == estrategia['padrao']:
                    return estrategia
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar estratégia: {e}")
            return None