"""Install a shared skill and CLI launcher without overwriting existing content."""
import argparse
import os
from pathlib import Path
import shlex
import sys

parser=argparse.ArgumentParser()
parser.add_argument('--target',choices=['codex','claude','hermes'],required=True)
parser.add_argument('--hermes-home',type=Path,help='Explicit Hermes profile root')
args=parser.parse_args()
repo=Path(__file__).resolve().parents[1]
root={'codex':Path.home()/'.codex','claude':Path.home()/'.claude','hermes':args.hermes_home or Path.home()/'.hermes'}[args.target]
dest=root/'skills/jev-relay';source=repo/'skills/jev-relay'
dest.parent.mkdir(parents=True,exist_ok=True)
if dest.is_symlink() and dest.resolve()==source:pass
elif dest.exists() or dest.is_symlink():raise SystemExit(f'Refusing to overwrite existing skill: {dest}')
else:dest.symlink_to(source,target_is_directory=True)
launcher=Path.home()/'.local/bin/jev-relay';launcher.parent.mkdir(parents=True,exist_ok=True)
content=f'#!/bin/sh\n# Managed by Jev Relay\nPYTHONPATH={shlex.quote(str(repo))} exec {shlex.quote(sys.executable)} -B -m jev_relay.cli "$@"\n'
if launcher.exists() and 'Managed by Jev Relay' not in launcher.read_text():raise SystemExit('Existing launcher is not owned by Jev Relay')
launcher.write_text(content);launcher.chmod(0o755)
print(f'Installed {args.target} skill: {dest}')
print(f'CLI: {launcher}')
