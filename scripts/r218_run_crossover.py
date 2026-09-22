#!/usr/bin/env python3
import argparse, hashlib, json, os, pathlib, platform, shutil, statistics, subprocess, time

PROTOCOL_SHA256='40d7153775efcc882410ff414a909ab6f6bab24193ecb2d746d7acdab33f6968'
ESTIMATOR_SHA256='86d9ca9b28e6fe2b6c74750a0b6ae4bba4c14f742ddc3f5f56bc7fb4ec9d8e27'
DATASET_SHA256='264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1'
BLOCKS=['U','C0','C1','C1','C0','U']
THREAD_KEYS=('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')

def sha256_path(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def read_json(p):
    return json.loads(pathlib.Path(p).read_text())

def write_json(p,obj):
    p=pathlib.Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')

def run_capture(args):
    return subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,check=True)

def telemetry(root, idx, cond):
    td=root/'telemetry'/f'block_{idx:02d}_{cond}'
    td.mkdir(parents=True,exist_ok=True)
    (td/'lscpu.json').write_text(run_capture(['lscpu','-J']).stdout)
    shutil.copy('/proc/cpuinfo',td/'proc_cpuinfo.txt')
    shutil.copy('/proc/self/status',td/'orchestrator_proc_self_status.txt')
    (td/'orchestrator_affinity.json').write_text(json.dumps({'sched_getaffinity':sorted(os.sched_getaffinity(0))})+'\n')
    (td/'taskset_orchestrator.txt').write_text(run_capture(['taskset','-pc',str(os.getpid())]).stdout)
    return td

def normalize_rows(report, block_index, condition):
    rows=[]
    for i,x in enumerate(report['results']['per_mlp']):
        reasons=[k for k in ('budget_exhausted','combined_budget_exhausted','time_exhausted','residual_wall_time_exhausted') if x.get(k)]
        if x.get('traceback'): reasons.append('traceback')
        rows.append({
            'block_index':block_index,'condition':condition,'mlp_index':i,'mlp_name':x.get('mlp_name'),
            'final_mse':x.get('final_layer_mse'),'measured_flops':x.get('flops_used'),
            'effective_compute':x.get('effective_compute'),
            'residual_wall_time_s':x.get('residual_wall_time_s'),'wall_time_s':x.get('wall_time_s'),
            'flopscope_backend_time_s':x.get('flopscope_backend_time_s'),'flopscope_overhead_time_s':x.get('flopscope_overhead_time_s'),
            'official_adjusted_score':x.get('adjusted_final_layer_score'),
            'status':'failed' if reasons else 'ok','failure_reasons':reasons,
        })
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--estimator',required=True)
    ap.add_argument('--protocol',required=True)
    ap.add_argument('--expected-panel',required=True)
    ap.add_argument('--out',required=True)
    ap.add_argument('--dataset',required=True)
    args=ap.parse_args()
    root=pathlib.Path(args.out); root.mkdir(parents=True,exist_ok=True)
    protocol=read_json(args.protocol); expected=read_json(args.expected_panel)
    gates={}
    gates['protocol_sha256']=(sha256_path(args.protocol)==PROTOCOL_SHA256)
    gates['expected_panel_static']=(expected.get('dataset',{}).get('sha256')==DATASET_SHA256 and expected.get('source',{}).get('sha256')==ESTIMATOR_SHA256 and len(expected.get('panel',[]))==50)
    gates['source_sha256']=(sha256_path(args.estimator)==ESTIMATOR_SHA256)
    gates['python']=(platform.python_version()=='3.11.16')
    try:
        import numpy, flopscope
        gates['numpy']=(numpy.__version__=='2.4.6')
        gates['flopscope']=(str(getattr(flopscope,'__version__','')).startswith('0.12.1'))
    except Exception:
        gates['numpy']=gates['flopscope']=False
    try:
        ver=json.loads(run_capture(['whest','version','--json']).stdout)
        gates['whestbench']=(ver.get('whestbench_version')=='0.16.1' or ver.get('version')=='0.16.1')
    except Exception:
        ver={}; gates['whestbench']=False
    gates['V26_STRASSEN']=(os.environ.get('V26_STRASSEN')=='4')
    gates['thread_env']=all(os.environ.get(k)=='1' for k in THREAD_KEYS)
    allowed=sorted(os.sched_getaffinity(0))
    gates['required_allowed_cpus']=(0 in allowed and 1 in allowed)
    gates['block_sequence']=(protocol.get('design',{}).get('block_sequence')==BLOCKS)
    gates['dataset_contract']=(protocol.get('contract_gates',{}).get('dataset_sha256')==DATASET_SHA256)
    gates['panel_static_identity']=(len(expected.get('panel',[]))==50 and [x['mlp_index'] for x in expected['panel']]==list(range(50)))
    gates['same_worker_single_job_design']=True
    preflight={
      'gates':gates,'all_pass':all(gates.values()),'allowed_cpu_affinity':allowed,
      'python':platform.python_version(),'platform':platform.platform(),'whest_version':ver,
      'thread_env':{k:os.environ.get(k) for k in THREAD_KEYS},'V26_STRASSEN':os.environ.get('V26_STRASSEN'),
      'github':{k:os.environ.get(k) for k in ('GITHUB_RUN_ID','GITHUB_RUN_ATTEMPT','GITHUB_JOB','RUNNER_NAME','RUNNER_OS','RUNNER_ARCH','ImageOS','ImageVersion')}
    }
    write_json(root/'preflight.json',preflight)
    if not preflight['all_pass']:
        write_json(root/'R218_RECEIPT.json',{'schema':'arc.whitebox.r218.crossover.v1','status':'INFRA_ERROR','decision':'PROTOCOL_INVALID_PRE_SCIENCE','preflight':preflight,'per_observation':[]})
        return 20

    expected_names=[x['mlp_name'] for x in expected['panel']]
    expected_flops=[int(x['measured_flops']) for x in expected['panel']]
    all_rows=[]; block_summaries=[]; runtime_gate_failures=[]
    for bi,cond in enumerate(BLOCKS,1):
        td=telemetry(root,bi,cond)
        child_status=td/'child_proc_self_status.txt'; child_taskset=td/'child_taskset.txt'
        report_path=root/f'block_{bi:02d}_{cond}_report.json'; stderr_path=root/f'block_{bi:02d}_{cond}_stderr.txt'
        exit_path=root/f'block_{bi:02d}_{cond}_exit.txt'
        whest=['whest','run','--estimator',args.estimator,'--dataset',args.dataset,'--split','mini','--streaming','--n-mlps','50','--runner','local','--flop-budget','2199023255552','--wall-time-limit','120','--residual-wall-time-limit','0.4','--max-threads','1','--format','json']
        if cond=='U': prefix=[]
        elif cond=='C0': prefix=['taskset','-c','0']
        elif cond=='C1': prefix=['taskset','-c','1']
        else: raise AssertionError(cond)
        cmd=prefix+['bash','-lc',f'cat /proc/self/status > {child_status}; taskset -pc $$ > {child_taskset}; exec "$@"','r218-child']+whest
        (root/f'block_{bi:02d}_{cond}_command.json').write_text(json.dumps(cmd)+'\n')
        t0=time.time()
        with report_path.open('w') as out, stderr_path.open('w') as err:
            cp=subprocess.run(cmd,stdout=out,stderr=err,text=True)
        dur=time.time()-t0; exit_path.write_text(str(cp.returncode)+'\n')
        if cp.returncode!=0 or not report_path.exists() or report_path.stat().st_size==0:
            write_json(root/'R218_RECEIPT.json',{'schema':'arc.whitebox.r218.crossover.v1','status':'INFRA_ERROR','decision':'BLOCK_EXECUTION_ERROR','failed_block':bi,'condition':cond,'exit_code':cp.returncode,'preflight':preflight,'per_observation':all_rows})
            return 21
        report=read_json(report_path)
        rows=normalize_rows(report,bi,cond)
        all_rows.extend(rows)
        cfg=report.get('run_config',{}); ds=cfg.get('dataset',{})
        names=[x['mlp_name'] for x in rows]; flops=[int(x['measured_flops']) for x in rows]
        block_gates={
          'count_50':len(rows)==50,
          'same_50_names_and_order':names==expected_names,
          'same_flop_accounting_per_mlp':flops==expected_flops,
          'dataset_sha256':ds.get('sha256')==DATASET_SHA256,
          'dataset_path':ds.get('path')==args.dataset,
          'flop_budget':cfg.get('flop_budget')==2199023255552,
          'residual_wall_time_limit_s':cfg.get('residual_wall_time_limit_s')==0.4,
          'width':cfg.get('width')==1024,'depth':cfg.get('depth')==16,
          'whestbench_version':report.get('whestbench_version')=='0.16.1',
        }
        if not all(block_gates.values()):
            runtime_gate_failures.append({'block_index':bi,'condition':cond,'gates':block_gates})
        failures=sum(x['status']=='failed' for x in rows)
        block_summaries.append({
          'block_index':bi,'condition':cond,'duration_s':dur,'exit_code':cp.returncode,'gates':block_gates,
          'failures':failures,'official_adjusted_score':report['results'].get('adjusted_final_layer_score'),
          'official_final_layer_mse':report['results'].get('final_layer_mse'),
          'mean_compute_utilization':report['results'].get('mean_compute_utilization'),
          'report_sha256':sha256_path(report_path),'stderr_sha256':sha256_path(stderr_path),
          'child_taskset':child_taskset.read_text().strip() if child_taskset.exists() else None,
        })
        write_json(root/'progress.json',{'completed_blocks':bi,'block_summaries':block_summaries,'runtime_gate_failures':runtime_gate_failures})
        if runtime_gate_failures:
            write_json(root/'R218_RECEIPT.json',{'schema':'arc.whitebox.r218.crossover.v1','status':'INFRA_ERROR','decision':'PROTOCOL_INVALID_RUNTIME_GATE','preflight':preflight,'runtime_gate_failures':runtime_gate_failures,'block_summaries':block_summaries,'per_observation':all_rows})
            return 22

    by_cond={c:[] for c in ('U','C0','C1')}
    for c in by_cond:
        blocks=[r for r in all_rows if r['condition']==c]
        assert len(blocks)==100
        per=[]
        for i in range(50):
            rr=[r for r in blocks if r['mlp_index']==i]
            assert len(rr)==2
            per.append(statistics.mean(float(r['residual_wall_time_s']) for r in rr))
        by_cond[c]=per
    deltas=[by_cond['C0'][i]-by_cond['C1'][i] for i in range(50)]
    primary_delta=statistics.median(deltas)
    cpu0_slower=sum(x>0 for x in deltas)
    c0_fail=sum(r['status']=='failed' for r in all_rows if r['condition']=='C0')
    c1_fail=sum(r['status']=='failed' for r in all_rows if r['condition']=='C1')
    failure_difference=c0_fail-c1_fail
    decision='GO_CPU0_SPECIFIC' if (primary_delta>=0.020 and cpu0_slower>=35 and failure_difference>=10) else 'NO_GO_CPU0_SPECIFIC'
    receipt={
      'schema':'arc.whitebox.r218.crossover.v1','job_id':'R218','status':'COMPLETE','decision':decision,
      'mode':'EXPOSED_PUBLIC_PANEL_RUNTIME_DIAGNOSTIC_NOT_INDEPENDENT_QUALITY_CONFIRMATION',
      'protocol_sha256':PROTOCOL_SHA256,'expected_panel_sha256':sha256_path(args.expected_panel),
      'source_sha256':ESTIMATOR_SHA256,'dataset_sha256':DATASET_SHA256,
      'preflight':preflight,'block_sequence':BLOCKS,'block_summaries':block_summaries,
      'analysis':{
        'primary_delta_s':primary_delta,'cpu0_slower_count':cpu0_slower,
        'c0_failures_across_two_blocks':c0_fail,'c1_failures_across_two_blocks':c1_fail,
        'failure_difference':failure_difference,
        'per_mlp_C0_mean_residual_s':by_cond['C0'],'per_mlp_C1_mean_residual_s':by_cond['C1'],'per_mlp_U_mean_residual_s':by_cond['U'],
        'per_mlp_C0_minus_C1_s':deltas,
        'go_thresholds':{'primary_delta_s_min':0.020,'cpu0_slower_count_min':35,'failure_difference_min':10}
      },
      'runtime_gate_failures':runtime_gate_failures,'per_observation':all_rows,
      'safety':{'retry':False,'rescue':False,'private_holdout':False,'submission':False}
    }
    write_json(root/'R218_RECEIPT.json',receipt)
    manifest={}
    for p in sorted(root.rglob('*')):
        if p.is_file() and p.name!='sha256.json': manifest[str(p.relative_to(root))]=sha256_path(p)
    write_json(root/'sha256.json',manifest)
    print(json.dumps({'status':'COMPLETE','decision':decision,'primary_delta_s':primary_delta,'cpu0_slower_count':cpu0_slower,'failure_difference':failure_difference,'block_summaries':block_summaries},sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
