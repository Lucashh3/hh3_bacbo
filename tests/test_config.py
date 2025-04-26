"""Testes para o gerenciador de configurações"""
import unittest
import os
import json
from src.config.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Criar arquivo de configuração temporário
        cls.test_config = {
            "aposta_base": 25,
            "aposta_empate": 10
        }
        with open('test_config.json', 'w') as f:
            json.dump(cls.test_config, f)

    @classmethod
    def tearDownClass(cls):
        os.remove('test_config.json')

    def test_carregar_config(self):
        """Testa o carregamento de configurações"""
        manager = ConfigManager()
        # Testa valores padrão
        self.assertEqual(manager.config['aposta_base'], 20)
        self.assertEqual(manager.config['aposta_empate'], 5)

if __name__ == '__main__':
    unittest.main()