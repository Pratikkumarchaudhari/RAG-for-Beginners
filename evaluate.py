"""Measure source hit rate and absent-question rejection; generation is optional."""
import argparse
import json
import time
from pathlib import Path
from rag.pipeline import LocalIndex, generate_answer

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', default='.rag_index')
    parser.add_argument('--top-k', type=int, default=3)
    parser.add_argument('--threshold', type=float, default=0.25)
    parser.add_argument('--generate', action='store_true')
    parser.add_argument('--model', default='qwen2.5:1.5b')
    parser.add_argument('--output', default='evaluation/results.json')
    args = parser.parse_args()
    index = LocalIndex(args.index)
    if not index.collection.count():
        parser.error('Build the index first with python ingestion_pipeline.py.')
    records = []
    for case in json.loads(Path('evaluation/questions.json').read_text()):
        start = time.perf_counter()
        hits = index.search(case['question'], args.top_k, args.threshold)
        record = {**case, 'sources': [h['source'] for h in hits],
                  'source_hit': case['expected_source'] in [h['source'] for h in hits] if case['answerable'] else None,
                  'retrieval_rejected': not hits}
        if args.generate:
            record['answer'] = generate_answer(case['question'], hits, args.model)
        record['seconds'] = round(time.perf_counter() - start, 3)
        records.append(record)
    positive = [r for r in records if r['answerable']]
    negative = [r for r in records if not r['answerable']]
    summary = {'source_hit_rate_at_k': sum(r['source_hit'] for r in positive) / len(positive),
               'absent_question_rejection_rate': sum(r['retrieval_rejected'] for r in negative) / len(negative),
               'top_k': args.top_k, 'threshold': args.threshold,
               'note': 'Source hit rate is not answer accuracy. Manually review generated claims and citations.'}
    output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({'summary': summary, 'records': records}, indent=2))
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()
