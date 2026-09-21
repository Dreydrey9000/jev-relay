"""Read a bounded local Messages snapshot without changing Messages or contacts."""
import argparse
import datetime
import json
from pathlib import Path
import sqlite3

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
database = Path.home() / 'Library/Messages/chat.db'
connection = sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)
connection.execute('PRAGMA query_only=ON')
rows = connection.execute('''
WITH ranked AS (
 SELECT c.ROWID chat_id,c.display_name,m.guid,m.text,m.date,m.is_from_me,h.id sender,
 ROW_NUMBER() OVER (PARTITION BY c.ROWID ORDER BY m.date DESC,m.ROWID DESC) rank
 FROM chat c JOIN chat_message_join cm ON cm.chat_id=c.ROWID
 JOIN message m ON m.ROWID=cm.message_id LEFT JOIN handle h ON h.ROWID=m.handle_id
 WHERE m.date > 0 AND COALESCE(m.associated_message_type,0)=0
)
SELECT chat_id,display_name,guid,text,date,is_from_me,sender FROM ranked WHERE rank=1 ORDER BY date DESC LIMIT 1000
''').fetchall()
items=[]
for chat,name,guid,body,date,own,sender in rows:
    seconds = date / 1_000_000_000 if date > 10**12 else date
    timestamp = datetime.datetime.fromtimestamp(seconds+978307200,datetime.timezone.utc).isoformat()
    items.append({'id':f'imessage:{chat}','source':'imessage','version':str(guid),'subject':name or 'Text conversation','sender':sender or ('You' if own else 'Unknown sender'),'snippet':(body or '[Text unavailable in plain-text field; open Messages to inspect.]')[:1200],'received_at':timestamp,'needs_reply':not bool(own)})
payload={'coverage':'Latest available non-reaction message per conversation, up to 1000 local Mac conversations; attachments and unavailable text excluded. Not a complete iCloud history.','items':items}
args.output.parent.mkdir(parents=True,exist_ok=True)
with args.output.open('x') as stream:
    args.output.chmod(0o600)
    json.dump(payload,stream)
print(json.dumps({'conversations':len(items),'possibly_unanswered':sum(i['needs_reply'] for i in items),'output_created':True}))
