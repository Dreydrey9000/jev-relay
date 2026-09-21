"""Run fixed, public synthetic cases through the actual router, including guards."""
import argparse
import json
from pathlib import Path
import statistics
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from jev_relay.router import route

parser=argparse.ArgumentParser()
parser.add_argument('--config',type=Path,required=True)
parser.add_argument('--cases',type=Path,default=Path(__file__).resolve().parents[1]/'eval/cases.json')
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--provider',choices=['local','jev'],default='local')
parser.add_argument('--ack-resource-warning',action='store_true')
args=parser.parse_args()
config=json.loads(args.config.read_text());records=[]
for case in json.loads(args.cases.read_text()):
    started=time.monotonic()
    result=route({k:case[k] for k in ['state','questions']},config,importance='important' if args.provider=='jev' else 'routine',cloud_allowed=args.provider=='jev',sensitive=False,warning_ack=args.ack_resource_warning)
    answer=result['answers'].get('decision',{})
    row={'id':case['id'],'group':case['group'],'gold':case['gold'],'choice':answer.get('choice'),'correct':answer.get('choice')==case['gold'],'seconds':round(time.monotonic()-started,3),'result':result}
    records.append(row)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(records,indent=2))
    print(row['id'],row['choice'],row['correct'],row['seconds'],flush=True)
    if len(records)>=2 and all(not r['result']['answers'] for r in records[-2:]):
        print('Stopping after two unavailable results.',flush=True);break
valid=[r for r in records if r['choice'] is not None]
summary={'provider':args.provider,'attempted':len(records),'valid':len(valid),'correct':sum(r['correct'] for r in valid),'accuracy':sum(r['correct'] for r in valid)/len(valid) if valid else None,'median_cold_roundtrip_seconds':statistics.median(r['seconds'] for r in valid) if valid else None,'scope':'Small synthetic pilot through router with a fresh local worker per call; not a warm GPU benchmark or deployment accuracy guarantee.'}
args.output.with_name(args.output.stem+'-summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))
