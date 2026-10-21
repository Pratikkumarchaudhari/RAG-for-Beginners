(function (root) {
  'use strict';
  const STOP = new Set('a an the is are was were to of in on for and or does do how what who when that it be can i we my our their its with from by as at this about please tell me explain often frequently much many should would could'.split(' '));
  const ALIASES = {authorizes:'approve',authorize:'approve',approves:'approve',approved:'approve',approval:'approve',approving:'approve',approvals:'approve',requests:'request',requesting:'request',reviewed:'review',reviews:'review',reviewing:'review',datasets:'dataset',records:'record',issues:'issue',values:'value',formats:'format',checks:'check',checking:'check',measures:'measure',measuring:'measure',required:'require',requires:'require',needed:'require',need:'require',contains:'include',contain:'include',includes:'include',include:'include',belong:'include',belongs:'include',information:'record',details:'record',escalated:'escalate',escalating:'escalate',escalation:'escalate',escalations:'escalate',addresses:'address',exists:'exist',existence:'exist',granted:'grant',granting:'grant',remove:'remove',removed:'remove',removing:'remove',removal:'remove',leaves:'leave',closing:'close',closed:'close',resolution:'resolve',resolved:'resolve'};
  function tokenize(text) {
    return (String(text).toLowerCase().match(/[a-z0-9]+/g) || [])
      .filter(t => !STOP.has(t)).map(t => ALIASES[t] || t);
  }
  function counts(words) { const result = new Map(); words.forEach(w => result.set(w,(result.get(w)||0)+1)); return result; }
  function rank(question, items) {
    const query = [...new Set(tokenize(question))];
    const docs = items.map(item => counts(tokenize(item.text)));
    const lengths = docs.map(doc => [...doc.values()].reduce((a,b)=>a+b,0));
    const average = lengths.reduce((a,b)=>a+b,0)/Math.max(1,items.length) || 1;
    return items.map((item,i) => {
      let score = 0;
      query.forEach(term => {
        const n = docs.filter(doc => doc.has(term)).length;
        const idf = Math.log(1+(items.length-n+0.5)/(n+0.5));
        const tf = docs[i].get(term)||0;
        score += idf * tf * 2.5 / (tf+1.5*(0.25+0.75*lengths[i]/average));
      });
      return {...item, score};
    }).sort((a,b)=>b.score-a.score);
  }
  function createAssistant(documents) {
    const docs = documents.map(doc => ({...doc, text:doc.text.replace(/^#.*$/gm,'').replace('Fictional learning material. Not an employer policy.','').trim()}));
    const vocabulary = new Set(docs.flatMap(d=>tokenize(d.text)));
    function answer(input) {
      const question = String(input||'').trim();
      const abstain = reason => ({question,status:'unsupported',answer:'I don’t have enough evidence in these sample documents to answer that question.',citations:[],reason});
      if(!question) return abstain('Enter a question about the sample governance procedures.');
      if(question.length>500) return abstain('Please keep the question under 500 characters.');
      const terms = [...new Set(tokenize(question))];
      if(!terms.length) return abstain('Try a more specific governance question.');
      const known = terms.filter(t=>vocabulary.has(t));
      // Conservative lexical gate: decline content terms not covered by the corpus.
      // This can reject paraphrases; it is not a guarantee of answer correctness.
      if(known.length<terms.length || !known.length) return abstain('The question includes concepts outside this small document collection. Try a suggested question or inspect the documents.');
      const ranked = rank(question,docs);
      const best = ranked[0];
      if(!best || best.score<0.15) return abstain('No sufficiently relevant passage was found.');
      const sentences = best.text.split(/(?<=[.!?])\s+/).filter(t=>t.trim());
      const candidates = rank(question,sentences.map((text,i)=>({text,position:i})));
      // Role questions need a role/action sentence, rather than a request checklist.
      candidates.forEach(candidate=>{
        if(/^who\b/i.test(question) && /\b(owner|administrator|steward|requesters)\b/i.test(candidate.text)) candidate.score+=1;
        if(/^who\b/i.test(question) && terms.includes('approve') && /\bapproves\b/i.test(candidate.text)) candidate.score+=3;
      });
      candidates.sort((a,b)=>b.score-a.score);
      const selected=candidates.filter(c=>c.score>0).slice(0,1);
      if(!selected.length) return abstain('No answer sentence was found.');
      // Return complete source sentences verbatim, never a fabricated completion.
      return {question,status:'answered',answer:selected.map(s=>s.text).join(' '),
        citations:[{source:best.source,title:best.title,text:best.text,excerpt:selected[0].text}],
        method:'Extractive answer using lexical retrieval; no language model'};
    }
    return {answer,documents:docs};
  }
  const api={createAssistant,tokenize};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  else root.GovernanceQA=api;
})(typeof globalThis!=='undefined'?globalThis:this);
