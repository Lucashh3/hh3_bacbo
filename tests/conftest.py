"""Configurações de fixtures para pytest"""
import pytest
from src.config.config_manager import ConfigManager
from src.core.estrategias import EstrategiaManager

@pytest.fixture
def config_manager():
    manager = ConfigManager()
    return manager

@pytest.fixture
def estrategia_manager():
    manager = EstrategiaManager()
    manager.estrategias = [
        {'padrao': ['A', 'A', 'V'], 'entrada': 'V', 'nome': 'Padrão 1'},
        {'padrao': ['V', 'V', 'A'], 'entrada': 'A', 'nome': 'Padrão 2'}
    ]
    return manager