import { Database } from 'bun:sqlite';
import { createAttention, attentionRoutes } from './engine/attention';
const service=createAttention(new Database(':memory:'),async path=>path==='profile'?{emailAddress:'synthetic@example.test'}:path.startsWith('threads?')?{threads:[{id:'abc'}]}:{id:'abc',messages:[{id:'123',internalDate:'1700000000000',labelIds:['INBOX'],snippet:'Synthetic example: Can you approve tomorrow’s agenda?',payload:{headers:[{name:'Subject',value:'SYNTHETIC · Workshop agenda'},{name:'From',value:'Example organizer'}]}}]});
const route=attentionRoutes(service);
Bun.serve({hostname:'127.0.0.1',port:5779,async fetch(req){const result=await route(req);if(result)return result;const path=new URL(req.url).pathname;const name=path==='/'?'attention.html':path.slice(1);if(!['attention.html','attention-ui.js','attention.css','attention-flow.svg','attention-walkthrough.mp3'].includes(name))return new Response('Not found',{status:404});return new Response(Bun.file(new URL('./engine/public/'+name,import.meta.url).pathname));}});
console.log('Synthetic QA preview: http://127.0.0.1:5779');
