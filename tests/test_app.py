"""UI integration test; model and semantic retrieval are explicitly stubbed."""
import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

class Collection:
    def count(self):
        return 3

class Index:
    collection = Collection()
    def search(self, *args):
        return [{'text':'The Data Owner approves access.', 'source':'access_management.md', 'page':1, 'similarity':0.7}]

class AppTests(unittest.TestCase):
    def test_question_answer_and_evidence(self):
        with patch('rag.pipeline.LocalIndex', return_value=Index()), patch('rag.pipeline.generate_answer', return_value='The Data Owner approves access [1].'):
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
            app.text_input(key='question').set_value('Who approves access?')
            app.button(key='ask').click().run()
            self.assertFalse(app.exception)
            self.assertTrue(any('The Data Owner approves' in item.value for item in app.markdown))
            self.assertEqual(app.expander[0].label, '[1] access_management.md — page 1 — similarity 0.7')

if __name__ == '__main__':
    unittest.main()
