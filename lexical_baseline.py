"""Dependency-free BM25 retrieval baseline; no generation or model downloads."""
import argparse,json,math,re
from collections import Counter
from pathlib import Path
from rag.pipeline import load_chunks

ROOT=Path(__file__).resolve().parent
STOP=set('a an the is are was were to of in on for and or does do how what who when that it'.split())

def tokens(text):
    return [x for x in re.findall(r'[a-z0-9]+',text.lower()) if x not in STOP]

def search(question,chunks,top_k=3,min_score=.2):
    if top_k<1:raise ValueError('top_k must be positive')
    if not chunks:return []
    docs=[Counter(tokens(c.text)) for c in chunks]
    lengths=[sum(d.values()) for d in docs];average=sum(lengths)/len(docs) or 1
    query=set(tokens(question));scores=[]
    for i,doc in enumerate(docs):
        score=0.
        for term in query:
            frequency=sum(term in d for d in docs)
            idf=math.log(1+(len(docs)-frequency+.5)/(frequency+.5))
            tf=doc[term]
            score+=idf*tf*2.5/(tf+1.5*(.25+.75*lengths[i]/average))
        if score>=min_score:scores.append(dict(source=chunks[i].source,position=chunks[i].position,score=round(score,4),text=chunks[i].text))
    return sorted(scores,key=lambda h:h['score'],reverse=True)[:top_k]

def evaluate(top_k=3):
    chunks=load_chunks(ROOT/'sample_documents');questions=json.loads((ROOT/'evaluation/questions.json').read_text())
    rows=[]
    for q in questions:
        hits=search(q['question'],chunks,top_k)
        passed=any(h['source']==q['expected_source'] for h in hits) if q['answerable'] else not hits
        rows.append({**q,'sources':[h['source'] for h in hits],'passed':passed})
    answerable=[r for r in rows if r['answerable']];absent=[r for r in rows if not r['answerable']]
    return dict(method='BM25 lexical baseline; NOT semantic embeddings or generation',top_k=top_k,min_score=.2,
        chunks=len(chunks),answerable_hits=sum(r['passed'] for r in answerable),answerable_total=len(answerable),
        absent_rejections=sum(r['passed'] for r in absent),absent_total=len(absent),results=rows)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--top-k',type=int,default=3)
    a=p.parse_args();result=evaluate(a.top_k)
    (ROOT/'evaluation/lexical_results.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
