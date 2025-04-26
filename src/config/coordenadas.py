"""Gerenciador de coordenadas para automação"""
import json
import logging
import os

logger = logging.getLogger(__name__)

class CoordenadasManager:
    """Gerencia as coordenadas de elementos na tela"""
    
    REQUIRED_COORDS = ['azul', 'vermelho', 'empate', 'ficha_5']
    
    def __init__(self):
        try:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            coordenadas_path = os.path.join(dir_path, 'coordenadas_bacbo.json')
            with open(coordenadas_path, 'r') as f:
                self.coordenadas = json.load(f)
            self._validar_coordenadas()
            logger.info("Coordenadas carregadas com sucesso")
        except FileNotFoundError:
            raise FileNotFoundError("Arquivo coordenadas_bacbo.json não encontrado")
        except json.JSONDecodeError:
            raise ValueError("Arquivo coordenadas_bacbo.json inválido")
    
    def _validar_coordenadas(self):
        """Valida as coordenadas obrigatórias"""
        for coord in self.REQUIRED_COORDS:
            if coord not in self.coordenadas:
                raise ValueError(f"Coordenada obrigatória faltando: {coord}")
            if not isinstance(self.coordenadas[coord], list) or len(self.coordenadas[coord]) != 2:
                raise ValueError(f"Coordenada {coord} inválida. Deve ser [x,y]")
            if self.coordenadas[coord] == [0, 0]:
                raise ValueError(f"Coordenada {coord} não configurada")