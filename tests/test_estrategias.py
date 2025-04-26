"""Testes unitários para o módulo de estratégias"""
import unittest
from src.core.estrategias import EstrategiaManager

class TestEstrategias(unittest.TestCase):
    def setUp(self):
        self.manager = EstrategiaManager()
        # Mock de estratégias para testes
        self.manager.estrategias = [
            {'padrao': ['A', 'A', 'V'], 'entrada': 'V', 'nome': 'Padrão 1'},
            {'padrao': ['V', 'V', 'A'], 'entrada': 'A', 'nome': 'Padrão 2'}
        ]

    def test_carregar_estrategias(self):
        """Testa se as estratégias são carregadas corretamente"""
        estrategias = self.manager.estrategias
        self.assertIsInstance(estrategias, list)
        self.assertEqual(len(estrategias), 2)
        for e in estrategias:
            self.assertIn('padrao', e)
            self.assertIn('entrada', e)

    def test_encontrar_estrategia(self):
        """Testa o reconhecimento de padrões"""
        test_cases = [
            (['A', 'A', 'V'], 'V'),
            (['V', 'V', 'A'], 'A'),
            (['A', 'V', 'A'], None),
            (['V', 'A', 'V'], None)
        ]
        
        for padrao, esperado in test_cases:
            with self.subTest(padrao=padrao):
                result = self.manager.encontrar_estrategia(padrao)
                if esperado:
                    self.assertIsNotNone(result)
                    self.assertEqual(result['entrada'], esperado)
                else:
                    self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()