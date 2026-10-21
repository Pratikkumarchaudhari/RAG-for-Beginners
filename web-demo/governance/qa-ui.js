'use strict';
const assistant=GovernanceQA.createAssistant(GOVERNANCE_DOCUMENTS);
const suggestions=[
  'Who approves access to a dataset?',
  'How often is access reviewed?',
  'What information belongs in a data issue record?',
  'When should a critical data issue be escalated?',
  'What does completeness measure?',
  'Does a postal code format check prove that an address exists?',
  'When should access be removed?',
  'What is the cafeteria lunch menu?'
];
const form=document.getElementById('question-form');
const input=document.getElementById('question');
const thread=document.getElementById('thread');
const status=document.getElementById('status');
function element(tag,className,text){const e=document.createElement(tag);if(className)e.className=className;if(text)e.textContent=text;return e;}
function ask(question){
  if(!question.trim()){status.textContent='Enter a question or select one below.';input.focus();return;}
  const result=assistant.answer(question);
  const exchange=element('article','exchange');
  const user=element('div','user-message');user.append(element('span','message-label','You'),element('p','',question));
  const response=element('div','answer-message');
  response.append(element('span','message-label',result.status==='answered'?'Answer from the documents':'Not covered by these documents'));
  response.append(element('p','answer-text',result.answer));
  if(result.status==='answered'){
    const citation=element('a','citation','[1] '+result.citations[0].source);
    citation.href='#doc-'+result.citations[0].source.replace(/\W/g,'-');
    citation.addEventListener('click',()=>{document.getElementById(citation.hash.slice(1)).open=true;});
    response.append(citation);
    const details=element('details','evidence');details.append(element('summary','','Inspect supporting document'));
    details.append(element('p','source-text',result.citations[0].text));response.append(details);
  }else response.append(element('p','answer-note',result.reason));
  exchange.append(user,response);thread.append(exchange);
  document.getElementById('welcome').hidden=true;
  status.textContent=result.status==='answered'?'Answer ready. One source cited.':'No supported answer. Try a suggested question.';
  input.value='';
  exchange.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'nearest'});
}
form.addEventListener('submit',e=>{e.preventDefault();ask(input.value);});
input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();form.requestSubmit();}});
suggestions.forEach(question=>{
  const button=element('button','suggestion',question);button.type='button';button.addEventListener('click',()=>ask(question));document.getElementById('suggestions').append(button);
});
assistant.documents.forEach(doc=>{
  const details=element('details','corpus-document');details.id='doc-'+doc.source.replace(/\W/g,'-');
  details.append(element('summary','',doc.title));details.append(element('p','source-text',doc.text));document.getElementById('documents').append(details);
});
document.getElementById('clear').addEventListener('click',()=>{thread.replaceChildren();document.getElementById('welcome').hidden=false;status.textContent='Conversation cleared.';input.value='';input.focus();});
