import unittest
from lexical_baseline import search
from rag.pipeline import Chunk

class BaselineTests(unittest.TestCase):
    def test_cites_matching_document(self):
        chunks=[Chunk('The data owner approves access','access.md',1,0),Chunk('Track quality issues','issues.md',1,0)]
        self.assertEqual(search('access approval',chunks)[0]['source'],'access.md')
    def test_absent_and_empty(self):
        self.assertEqual(search('cafeteria', [Chunk('data quality','q.md',1,0)]),[])
        self.assertEqual(search('data',[]),[])
    def test_bad_top_k(self):
        with self.assertRaises(ValueError):search('data',[],0)
