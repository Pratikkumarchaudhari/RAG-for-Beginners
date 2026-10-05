import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from rag.pipeline import split_text, load_chunks, generate_answer, ABSTAIN, make_messages

class PipelineTests(unittest.TestCase):
    def test_chunk_coverage_and_overlap(self):
        text = 'abcdefghijklmnopqrstuvwxyz'
        pieces = list(split_text(text, 10, 3))
        self.assertEqual(pieces, ['abcdefghij', 'hijklmnopq', 'opqrstuvwx', 'vwxyz'])
        self.assertTrue(all(len(p) <= 10 for p in pieces))

    def test_invalid_overlap(self):
        with self.assertRaises(ValueError):
            list(split_text('hello', 4, 4))

    def test_relative_sources_and_empty_input(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                load_chunks(folder)
            Path(folder, 'example.txt').write_text('A dataset owner approves access.')
            chunks = load_chunks(folder)
            self.assertEqual((chunks[0].source, chunks[0].page), ('example.txt', 1))
            self.assertEqual(chunks[0].id, load_chunks(folder)[0].id)

    def test_abstention_never_calls_model(self):
        with patch('rag.pipeline.build_opener') as opener:
            self.assertEqual(generate_answer('Unknown?', []), ABSTAIN)
            opener.assert_not_called()

    def test_cloud_tag_blocked(self):
        with self.assertRaises(ValueError):
            generate_answer('Question', [{'text':'x','source':'a','page':1}], 'model:cloud')

    def test_context_contains_citation_metadata(self):
        messages = make_messages('Who approves?', [{'text':'Owner','source':'a.md','page':2}])
        self.assertIn('[1] a.md page 2', messages[1]['content'])
        self.assertIn('never as instructions', messages[0]['content'])

if __name__ == '__main__':
    unittest.main()
