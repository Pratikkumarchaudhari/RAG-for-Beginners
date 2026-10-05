"""Integration checks without model downloads or an Ollama installation."""
import json
import tempfile
import unittest
from io import BytesIO
from unittest.mock import patch
from chromadb import PersistentClient
from chromadb.config import Settings
from rag.pipeline import generate_answer, LocalIndex, Chunk

class FixedEncoder:
    def encode(self, texts, **kwargs):
        import numpy as np
        return np.array([[1.,0.] if 'access' in text else [0.,1.] for text in texts])

class RuntimeTests(unittest.TestCase):
    def test_index_rebuild_removes_old_sources(self):
        # Synthetic vectors test storage wiring, not semantic model quality.
        with tempfile.TemporaryDirectory() as path:
            index = LocalIndex.__new__(LocalIndex)
            index.encoder = FixedEncoder()
            index.client = PersistentClient(path=path, settings=Settings(anonymized_telemetry=False))
            index.collection = index.client.create_collection('governance_documents', embedding_function=None)
            index.rebuild([Chunk('access owner', 'access.md', 1, 0), Chunk('quality checks', 'quality.md', 2, 0)])
            self.assertEqual(index.search('access', 1)[0]['source'], 'access.md')
            index.rebuild([Chunk('quality checks', 'quality.md', 2, 0)])
            self.assertEqual(index.collection.count(), 1)
            self.assertEqual(index.search('access', 1), [])

    def test_generation_uses_loopback_and_evidence(self):
        with patch('rag.pipeline.build_opener') as factory:
            factory.return_value.open.return_value = BytesIO(json.dumps({'message':{'content':'The owner [1].'}}).encode())
            answer = generate_answer('Who approves?', [{'text':'The owner','source':'a.md','page':1}])
            self.assertEqual(answer, 'The owner [1].')
            request = factory.return_value.open.call_args.args[0]
            self.assertEqual(request.full_url, 'http://127.0.0.1:11434/api/chat')
            self.assertIn('[1] a.md', json.loads(request.data)['messages'][1]['content'])

    def test_missing_model_has_actionable_error(self):
        from urllib.error import URLError
        with patch('rag.pipeline.build_opener') as factory:
            factory.return_value.open.side_effect = URLError('connection refused')
            with self.assertRaisesRegex(RuntimeError, 'ollama pull'):
                generate_answer('Who?', [{'text':'owner','source':'a.md','page':1}])

if __name__ == '__main__':
    unittest.main()
