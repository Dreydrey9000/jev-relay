import { Database } from 'bun:sqlite';

export const labels = ['review', 'important', 'not_important', 'ignored'] as const;
export function gmailItem(thread: any, account: string) {
  const messages = (thread.messages || []).filter((m: any) => !(m.labelIds || []).includes('DRAFT'))
    .sort((a: any, b: any) => Number(a.internalDate) - Number(b.internalDate));
  if (!messages.length || !/^[a-zA-Z0-9]+$/.test(thread.id || '')) return null;
  const latest = messages.at(-1);
  const header = (name: string) => String((latest.payload?.headers || []).find((h: any) => h.name.toLowerCase() === name)?.value || '').slice(0, 300);
  const sent = (latest.labelIds || []).includes('SENT');
  return { id: `gmail:${account}:${thread.id}`, source: 'gmail', account, version: String(latest.id),
    subject: header('subject') || '(No subject)', sender: header('from'), snippet: String(latest.snippet || '').slice(0, 1200),
    received_at: new Date(Number(latest.internalDate)).toISOString(), needs_reply: !sent,
    reason: sent ? 'Latest message in this Gmail thread is sent by you.' : 'Latest message in this Gmail thread is incoming; a reply may be needed.',
    url: `https://mail.google.com/mail/?authuser=${encodeURIComponent(account)}#all/${thread.id}` };
}

export function createAttention(database: Database, gmail: (path: string) => Promise<any>) {
  database.exec(`CREATE TABLE IF NOT EXISTS attention_items (id TEXT PRIMARY KEY, version TEXT NOT NULL, source TEXT NOT NULL, data TEXT NOT NULL, label TEXT NOT NULL DEFAULT 'review', updated_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS attention_state (key TEXT PRIMARY KEY, value TEXT NOT NULL);`);
  let syncing = false;
  const state = (key: string) => { const row = database.query('SELECT value FROM attention_state WHERE key=?').get(key) as any; return row ? JSON.parse(row.value) : null; };
  const save = (key: string, value: any) => database.query('INSERT OR REPLACE INTO attention_state VALUES (?,?)').run(key, JSON.stringify(value));
  function upsert(item: any) {
    const old = database.query('SELECT version,label FROM attention_items WHERE id=?').get(item.id) as any;
    const label = old?.version === item.version ? old.label : 'review';
    database.query('INSERT OR REPLACE INTO attention_items VALUES (?,?,?,?,?,?)').run(item.id, item.version, item.source, JSON.stringify(item), label, new Date().toISOString());
  }
  async function sync(reset: boolean) {
    if (syncing) return { busy: true };
    syncing = true;
    try {
      const profile = await gmail('profile');
      if (!profile.emailAddress) throw new Error('account_missing');
      const prior = state('gmail');
      const account = String(profile.emailAddress);
      const cursor = !reset && prior?.account === account ? prior.next_page : null;
      const params = new URLSearchParams({maxResults: '30', q: '-in:spam -in:trash'});
      if (cursor) params.set('pageToken', cursor);
      const page = await gmail(`threads?${params}`);
      let imported = 0;
      for (const row of page.threads || []) {
        const item = gmailItem(await gmail(`threads/${encodeURIComponent(row.id)}?format=metadata&metadataHeaders=From&metadataHeaders=Subject`), account);
        if (item) { upsert(item); imported++; }
      }
      save('gmail', {account, next_page: page.nextPageToken || null, imported, last_success: new Date().toISOString(), error: null, history_complete: !page.nextPageToken});
      return {imported};
    } catch {
      save('gmail', {...state('gmail'), error: 'Email sync failed. Retry or reconnect the existing Gmail connection. Saved items remain available.'});
      throw new Error('sync_failed');
    } finally { syncing = false; }
  }
  function list(filter = 'attention', offset = 0) {
    const rows = database.query('SELECT data,label,updated_at FROM attention_items ORDER BY json_extract(data,\'$.received_at\') DESC LIMIT 5000').all() as any[];
    const items = rows.map(r => ({...JSON.parse(r.data), label: r.label, updated_at: r.updated_at}));
    const visible = items.filter(item => filter === 'all' || (filter === 'attention' ? item.label === 'important' || (item.label === 'review' && item.needs_reply) : filter === 'unanswered' ? item.needs_reply && !['ignored','not_important'].includes(item.label) : item.label === filter));
    return {items: visible.slice(offset, offset + 50), total: visible.length, next_offset: offset + 50 < visible.length ? offset + 50 : null,
      stored: items.length, capped: items.length === 5000, gmail: state('gmail'), texts: state('texts'), syncing,
      model: 'Rules and your review. No local model or paid Jev calls.', automatic_delivery: false};
  }
  function mark(id: string, label: string, version?: string) {
    if (!(labels as readonly string[]).includes(label)) throw new Error('invalid_label');
    if (version !== undefined) return database.query('UPDATE attention_items SET label=?,updated_at=? WHERE id=? AND version=?').run(label,new Date().toISOString(),id,version).changes;
    return database.query('UPDATE attention_items SET label=?,updated_at=? WHERE id=?').run(label,new Date().toISOString(),id).changes;
  }
  function importTexts(payload: any) {
    if (!payload || !Array.isArray(payload.items) || payload.items.length > 1000) throw new Error('invalid_import');
    const checked = payload.items.map((item: any) => {
      if (item.source !== 'imessage' || typeof item.id !== 'string' || !item.id.startsWith('imessage:') || typeof item.version !== 'string' || typeof item.needs_reply !== 'boolean' || !Number.isFinite(Date.parse(item.received_at))) throw new Error('invalid_import');
      return {id: item.id.slice(0,300), source:'imessage', account:'local-mac',version:item.version.slice(0,150), subject:String(item.subject || 'Text conversation').slice(0,300), sender:String(item.sender || '').slice(0,300),snippet:String(item.snippet || '').slice(0,1200), received_at:item.received_at, needs_reply:item.needs_reply, reason:item.needs_reply ? 'Latest available text is incoming; check the conversation before replying.' : 'Latest available text is outgoing.',url:null};
    });
    database.transaction(() => { checked.forEach(upsert); save('texts',{last_success:new Date().toISOString(),imported:checked.length,coverage: String(payload.coverage || 'Available local Messages history').slice(0,200)}); })();
    return {imported:checked.length};
  }
  return {sync,list,mark,importTexts};
}

export function attentionRoutes(service: ReturnType<typeof createAttention>) {
  return async (req: Request): Promise<Response | null> => {
    const url = new URL(req.url), path = url.pathname;
    if (!path.startsWith('/api/attention/')) return null;
    const json = (body: any, status=200) => Response.json(body,{status,headers:{'cache-control':'no-store'}});
    // The host's existing login gate must run before this handler.
    if (req.method !== 'GET') {
      const origin = req.headers.get('origin');
      const allowed = origin === url.origin || (['dreyos.dreytools.com','dreyos.dreythomas.com'].includes(url.hostname) && origin === `https://${url.hostname}`);
      if (!origin || !allowed || req.headers.get('content-type')?.split(';')[0] !== 'application/json') return json({error:'origin_required'},403);
    }
    try {
      if (path === '/api/attention/items' && req.method === 'GET') {
        const filter=url.searchParams.get('filter') || 'attention';
        const offset=Number(url.searchParams.get('offset') || 0);
        if (!['attention','unanswered','all',...labels].includes(filter) || !Number.isInteger(offset) || offset<0 || offset>5000) return json({error:'invalid_filter'},400);
        return json(service.list(filter,offset));
      }
      if (Number(req.headers.get('content-length') || 0)>2048) return json({error:'too_large'},413);
      const raw=await req.text();
      if(raw.length>2048) return json({error:'too_large'},413);
      const body=JSON.parse(raw || '{}');
      if(path==='/api/attention/sync' && req.method==='POST') return json(await service.sync(body.reset === true));
      if(path==='/api/attention/mark' && req.method==='POST') {
        if(typeof body.id!=='string' || body.id.length>300 || typeof body.version!=='string') return json({error:'invalid_item'},400);
        return service.mark(body.id,body.label,body.version) ? json({saved:true}) : json({error:'item_changed_refresh'},409);
      }
      return json({error:'not_found'},404);
    } catch(e) { return json({error: e instanceof Error && e.message==='sync_failed' ? 'sync_failed' : 'invalid_request'}, e instanceof Error && e.message==='sync_failed' ? 503 : 400); }
  };
}
