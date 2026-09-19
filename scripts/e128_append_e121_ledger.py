from pathlib import Path
import csv

p=Path('research/ledger.csv')
with p.open(newline='',encoding='utf-8') as f:
    ids=[r['id'] for r in csv.DictReader(f)]
if 'E121' in ids:
    print('E121 already present; no-op')
    raise SystemExit(0)
row='E121,DONE,source_memory,"Haar two-plane cyclic orbit preserves shared source dependence through every ReLU layer",same_node_iid_spherical,exact_8d_candidate_over_iid,"Exact 8-D block-stress pooled candidate/iid MSE ratio <=0.90; deterministic replay; target-free; all-in utilization <=0.13",0,0,"2-D candidate/iid=2.7877903200189265e-05; 8-D candidate/iid=11.435172907952149; production all-in=275184628736 FLOPs; utilization=0.12513948092237115; deterministic replay exact; source audit PASS",DROP,"TERMINAL NO-GO. Frozen protocol baa802af0b11152389c7f6229648f9212d8257ff; authoritative receipt e2c7473a2919b4444daa581b14d1ed706960f7d8; run 35460988924 job 105944694427 artifact 10588818925 sha256 fb49a9be2945d0ffb3c8aaad3ae59600fd7cdc7493fd8959666319284632d836. Exact 8-D gate failed: low-dimensional orbit correlation collapses effective multi-source coverage. No benchmark/public/scorer/holdout/full, no rerun/rescue. Closed fingerprint: no P/M rebalance, seed/phase randomization, weighting or fitted correction. Successor E122 reserved for source-state dimension >2 or adaptive algebraic compression."\n'
with p.open('a',encoding='utf-8') as f:
    f.write(row)
print('appended E121 canonical ledger row')
