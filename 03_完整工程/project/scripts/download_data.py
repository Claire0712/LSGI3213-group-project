"""Re-fetch the exact public inputs only if absent; verify SHA-256 from manifest."""
from pathlib import Path
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[1]
for item in json.loads((ROOT/'data/source_manifest.json').read_text()):
    target=ROOT/'data/raw'/item['file']
    if not target.exists():subprocess.run(['curl','-fL','--retry','2',item['url'],'-o',str(target)],check=True)
    assert hashlib.sha256(target.read_bytes()).hexdigest()==item['sha256'],item['file']
    print('Verified',item['file'])
