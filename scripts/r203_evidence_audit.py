#!/usr/bin/env python3
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('artifact_root', type=Path)
    ap.add_argument('--zip', dest='zip_path', type=Path)
    ap.add_argument('--expected-zip-sha256')
    args=ap.parse_args()
    root=args.artifact_root
    art=root/'e173_artifacts'
    out={}
    if args.zip_path:
        got=sha256(args.zip_path)
        out['artifact_zip']={'path':str(args.zip_path),'sha256':got,'expected':args.expected_zip_sha256,'match':(got==args.expected_zip_sha256 if args.expected_zip_sha256 else None),'size_bytes':args.zip_path.stat().st_size}
    sha_map=json.loads((art/'sha256.json').read_text())
    bad=[]
    for rel,exp in sha_map.items():
        p=root/rel
        if not p.is_file(): bad.append([rel,'MISSING']); continue
        got=sha256(p)
        if got!=exp: bad.append([rel,got])
    out['sha256_map']={'entries':len(sha_map),'all_verified':not bad,'bad':bad}

    manifest=json.loads((root/'e173_vector_manifest.json').read_text())
    vec_bad=[]; rows=[]
    for rec in manifest['records']:
        loaded={}
        for ent in rec['payloads']:
            p=root/ent['path']
            if not p.is_file(): vec_bad.append([rec['mlp_name'],ent['path'],'missing']); continue
            a=np.load(p,allow_pickle=False); loaded[p.stem]=a
            if list(a.shape)!=ent['shape']: vec_bad.append([rec['mlp_name'],ent['path'],'shape'])
            if str(a.dtype)!=ent['dtype']: vec_bad.append([rec['mlp_name'],ent['path'],'dtype'])
            if a.nbytes!=ent['nbytes']: vec_bad.append([rec['mlp_name'],ent['path'],'nbytes'])
            if sha256(p)!=ent['file_sha256']: vec_bad.append([rec['mlp_name'],ent['path'],'file_sha256'])
            raw=hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
            if raw!=ent['raw_array_sha256']: vec_bad.append([rec['mlp_name'],ent['path'],'raw_array_sha256'])
        t=loaded['target_all_layer_means'].astype(np.float64)
        p=loaded['parent_prediction'].astype(np.float64)
        a=loaded['ago_prediction'].astype(np.float64)
        pmse=float(np.mean((p[-1]-t[-1])**2)); amse=float(np.mean((a[-1]-t[-1])**2))
        rows.append({'mlp_name':rec['mlp_name'],'parent_raw_mse':pmse,'ago_raw_mse':amse,'delta':pmse-amse})
    out['vectors']={'records':len(manifest['records']),'all_verified':not vec_bad,'bad':vec_bad,'per_mlp':rows}

    parent=json.loads((art/'parent_report.json').read_text()); ago=json.loads((art/'ago_report.json').read_text()); summary=json.loads((art/'E173_SUMMARY.json').read_text())
    def norm(rep):
        r=rep['results']; m=r['mean_score_multiplier']; checks=[math.isclose(r['adjusted_final_layer_score'],r['final_layer_mse']*m,rel_tol=0,abs_tol=1e-18)]
        checks += [math.isclose(x['adjusted_final_layer_score'],x['final_layer_mse']*m,rel_tol=0,abs_tol=1e-18) for x in r['per_mlp']]
        return m,all(checks)
    pm,pok=norm(parent); am,aok=norm(ago)
    pvals=np.array([x['parent_raw_mse'] for x in rows]); avals=np.array([x['ago_raw_mse'] for x in rows]); d=pvals-avals
    panel={'mean_parent_raw_mse':float(pvals.mean()),'mean_ago_raw_mse':float(avals.mean()),'ago_over_parent':float(avals.mean()/pvals.mean()),'improvement_fraction':float(1-avals.mean()/pvals.mean()),'improve_count':int(np.sum(avals<pvals)),'paired_delta_mean':float(d.mean()),'paired_delta_se':float(np.std(d,ddof=1)/np.sqrt(len(d)))}
    out['normalization']={'parent_multiplier':pm,'ago_multiplier':am,'parent_adjusted_equals_raw_times_multiplier':pok,'ago_adjusted_equals_raw_times_multiplier':aok,'history_rule':'If a history row stores adjusted_final_layer_score, divide by mean_score_multiplier (0.1) to recover raw final_layer_mse; do not compare adjusted scores directly to raw MSE.'}
    out['panel']=panel
    out['summary_panel_matches']=all([math.isclose(panel['mean_parent_raw_mse'],summary['panel']['mean_parent_final_layer_mse'],rel_tol=1e-7,abs_tol=1e-12),math.isclose(panel['mean_ago_raw_mse'],summary['panel']['mean_ago_final_layer_mse'],rel_tol=1e-7,abs_tol=1e-12),math.isclose(panel['ago_over_parent'],summary['panel']['ago_over_parent'],rel_tol=1e-7,abs_tol=1e-12)])
    out['existing_checks']={k:int((art/f'{k}.exit').read_text().strip()) for k in ['focused_tests','parent_validate','ago_validate','parent_run','ago_run','summarize']}
    out['existing_checks']['focused_tests_tail']=(art/'focused_tests.log').read_text(errors='replace').strip().splitlines()[-1]
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__': main()
