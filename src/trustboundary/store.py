from __future__ import annotations
import json
from pathlib import Path
from typing import Any,cast
class JsonStore:
    def __init__(self,workspace:Path)->None:
        self.workspace=workspace.resolve()
        if not (self.workspace/'workspace.json').is_file():raise FileNotFoundError('workspace.json not found')
        legacy=self.workspace/'trustboundary.json';namespace=self.workspace/'trustboundary';self.path=legacy if legacy.exists() else namespace/'state.json' if namespace.is_dir() else legacy
        if not self.path.exists():self.save({'schema_version':'0.3','nodes':[],'transitions':[],'assertions':[],'candidates':[],'identity_provenance':[],'mtls_identities':[],'assertion_results':[]})
    def load(self)->dict[str,Any]:
        data=cast(dict[str,Any],json.loads(self.path.read_text(encoding='utf-8')));data.setdefault('identity_provenance',[]);data.setdefault('mtls_identities',[]);data.setdefault('assertion_results',[]);return data
    def save(self,data:dict[str,Any])->None:
        t=self.path.with_suffix('.tmp');t.write_text(json.dumps(data,indent=2,default=str),encoding='utf-8');t.replace(self.path)
