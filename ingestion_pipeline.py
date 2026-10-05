"""Build the local index. Replaces the original paid embedding import."""
import argparse
from rag.pipeline import LocalIndex, load_chunks

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--documents', default='sample_documents')
    parser.add_argument('--index', default='.rag_index')
    parser.add_argument('--chunk-size', type=int, default=600)
    parser.add_argument('--overlap', type=int, default=100)
    args = parser.parse_args()
    chunks = load_chunks(args.documents, args.chunk_size, args.overlap)
    print(f'Indexed {LocalIndex(args.index).rebuild(chunks)} passages from {args.documents}.')

if __name__ == '__main__':
    main()
