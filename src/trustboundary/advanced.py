from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any
from .models import Node,NodeType,Transition,TrustAssertion
ASSERTION_LIBRARY={"ONLY_GATEWAY_CAN_REACH_BACKEND":"Backend network paths must traverse an approved gateway or proxy.","JWT_VALIDATED_BEFORE_IDENTITY_HEADER":"JWT identity must be validated before a trusted identity header is emitted.","INTERNAL_SERVICE_IDENTITY_REQUIRES_MTLS":"Internal service identity must be authenticated with mTLS or an equivalent cryptographic identity.","EXTERNAL_CLIENT_CANNOT_SET_TRUSTED_IDENTITY":"Externally controlled input must not directly establish a trusted internal identity.","REVOKED_IDENTITY_MUST_NOT_PROPAGATE":"Revoked identity state must not continue across downstream trust transitions."}
class TrustIntelligence:
    def __init__(self,engine:Any)->None:self.engine=engine
    def architecture_reconstruction_v2(self)->dict[str,Any]:
        data=self.engine.store.load();nodes={x['node_id']:Node.model_validate(x) for x in data['nodes']};edges=[]
        for raw in data['transitions']:
            t=Transition.model_validate(raw);basis=[]
            if t.input_name:basis.append(f'input:{t.input_name}')
            if t.output_name:basis.append(f'output:{t.output_name}')
            if t.metadata.get('source'):basis.append(f"source:{t.metadata['source']}")
            status='OBSERVED' if t.evidence_ids and t.verified is not None else 'INFERRED';edges.append({'transition_id':t.transition_id,'source':t.source_node_id,'target':t.target_node_id,'status':status,'confidence':.9 if status=='OBSERVED' else (.72 if basis else .5),'evidence_ids':t.evidence_ids,'basis':basis,'counter_evidence':['Unmodeled infrastructure may alter the effective path.'] if status=='INFERRED' else []})
        return {'nodes':[x.model_dump(mode='json') for x in nodes.values()],'candidate_chains':self.engine.proxy_chains(),'edges':edges,'principle':'Architecture inference does not establish exploitability.'}
    def identity_provenance(self)->list[dict[str,Any]]:
        data=self.engine.store.load();out=[]
        for raw in data['transitions']:
            t=Transition.model_validate(raw)
            if t.data_type.casefold() not in {'identity','header','jwt','token','credential','mtls'}:continue
            out.append({'identity_input':t.input_name,'identity_output':t.output_name,'origin':t.source_node_id,'consumer':t.target_node_id,'transformation':t.transformation,'validated':t.verified is True,'validator':t.metadata.get('validator'),'evidence_ids':t.evidence_ids,'status':'OBSERVED' if t.evidence_ids else 'INFERRED','confidence':.9 if t.evidence_ids and t.verified is not None else .6})
        data['identity_provenance']=out;self.engine.store.save(data);return out
    def mtls_identity(self,*,node_id:str,spiffe_id:str|None=None,san:list[str]|None=None,trust_domain:str|None=None,evidence_ids:list[str]|None=None)->dict[str,Any]:
        data=self.engine.store.load()
        if node_id not in {x['node_id'] for x in data['nodes']}:raise KeyError(node_id)
        record={'identity_id':'MTLS-'+hashlib.sha256(f'{node_id}:{spiffe_id}:{san}:{trust_domain}'.encode()).hexdigest()[:12],'node_id':node_id,'spiffe_id':spiffe_id,'san':san or [],'trust_domain':trust_domain,'evidence_ids':evidence_ids or [],'status':'OBSERVED' if evidence_ids else 'INFERRED','private_key_stored':False};records=data['mtls_identities']
        for i,x in enumerate(records):
            if x['identity_id']==record['identity_id']:records[i]=record;break
        else:records.append(record)
        self.engine.store.save(data);return record
    def import_cloud_config(self,path:Path)->dict[str,int]:
        if not path.is_file() or path.is_symlink():raise ValueError('cloud config must be a regular non-symlink JSON file')
        if path.stat().st_size>10*1024*1024:raise ValueError('cloud config exceeds size limit')
        payload=json.loads(path.read_text(encoding='utf-8'));objects=payload if isinstance(payload,list) else payload.get('resources',[]) if isinstance(payload,dict) else []
        if not isinstance(objects,list):raise ValueError('cloud config resources must be a list')
        nodes=transitions=0
        for obj in objects:
            if not isinstance(obj,dict):continue
            provider=str(obj.get('provider','unknown')).casefold();rtype=str(obj.get('type','resource'));name=str(obj.get('name',rtype));rid='cloud-'+hashlib.sha256(f'{provider}:{rtype}:{name}'.encode()).hexdigest()[:12];kind=NodeType.GATEWAY if any(x in rtype.casefold() for x in ('gateway','alb','loadbalancer','cloudfront','apim','proxy')) else NodeType.SERVICE
            self.engine.add_node(Node(node_id=rid,name=name,node_type=kind,public_reachable=bool(obj.get('public',False)),metadata={'provider':provider,'resource_type':rtype,'import_only':True}));nodes+=1
            for target in obj.get('targets',[]) if isinstance(obj.get('targets'),list) else []:
                tid='cloud-'+hashlib.sha256(f'target:{target}'.encode()).hexdigest()[:12];self.engine.add_node(Node(node_id=tid,name=str(target),node_type=NodeType.SERVICE,metadata={'provider':provider,'import_only':True}));self.engine.add_transition(Transition(transition_id='route-'+hashlib.sha256(f'{rid}:{tid}'.encode()).hexdigest()[:12],source_node_id=rid,target_node_id=tid,data_type='network_path',verified=None,metadata={'source':'cloud_config_import','provider':provider}));transitions+=1
        return {'nodes':nodes,'transitions':transitions}
    def install_assertion_library(self,node_id:str)->list[str]:
        ids=[]
        for name,statement in ASSERTION_LIBRARY.items():
            aid=f'LIB-{name}';self.engine.add_assertion(TrustAssertion(assertion_id=aid,node_id=node_id,statement=statement,basis='built-in auditable trust assertion library',metadata={'library_rule':name}));ids.append(aid)
        return ids
    def evaluate_assertions(self)->list[dict[str,Any]]:
        data=self.engine.store.load();nodes={x['node_id']:Node.model_validate(x) for x in data['nodes']};transitions=[Transition.model_validate(x) for x in data['transitions']];gateways={n.node_id for n in nodes.values() if n.node_type in {NodeType.GATEWAY,NodeType.PROXY}};mtls_nodes={x['node_id'] for x in data.get('mtls_identities',[]) if x.get('evidence_ids')};results=[]
        for raw in data['assertions']:
            a=TrustAssertion.model_validate(raw);rule=a.metadata.get('library_rule');status='UNKNOWN';evidence=[];counter=[]
            if rule=='ONLY_GATEWAY_CAN_REACH_BACKEND':
                alternate=[x for x in self.engine.direct_origin_paths() if x['target']==a.node_id]
                if alternate:status='HYPOTHESIS';counter=['A modeled alternate path reaches the target without a gateway.']
                elif gateways:status='INFERRED';evidence=['Modeled paths include gateway/proxy nodes; absence of alternate evidence is not proof.']
            elif rule=='JWT_VALIDATED_BEFORE_IDENTITY_HEADER':
                relevant=[t for t in transitions if t.target_node_id==a.node_id and t.data_type.casefold() in {'jwt','identity','header'}]
                if any(t.verified is False for t in relevant):status='HYPOTHESIS';counter=['An identity-bearing transition is explicitly unverified.']
                elif relevant and all(t.verified is True for t in relevant):status='OBSERVED';evidence=[e for t in relevant for e in t.evidence_ids]
            elif rule=='INTERNAL_SERVICE_IDENTITY_REQUIRES_MTLS':status='OBSERVED' if a.node_id in mtls_nodes else 'UNKNOWN';evidence=['Evidence-backed mTLS identity exists.'] if status=='OBSERVED' else []
            results.append({'assertion_id':a.assertion_id,'rule':rule,'status':status,'evidence':evidence,'counter_evidence':counter,'automatic_exploitability':False})
        data['assertion_results']=results;self.engine.store.save(data);return results
