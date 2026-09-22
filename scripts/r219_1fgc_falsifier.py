#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
import hashlib, json, math
from itertools import product
from pathlib import Path

OUT=Path("r219-result.json")
N=1024; L=16; Q=8; B=2**41

def law_parity():
    pts=[s for s in product((-1,1), repeat=4) if math.prod(s)==1]
    return [(s,Fraction(1,len(pts))) for s in pts]

def law_ind():
    pts=list(product((-1,1), repeat=4))
    return [(s,Fraction(1,len(pts))) for s in pts]

def marginal(law,i):
    d={}
    for s,p in law: d[s[i]]=d.get(s[i],Fraction(0))+p
    return tuple(sorted(d.items()))
def pairlaw(law,i,j):
    d={}
    for s,p in law: d[(s[i],s[j])]=d.get((s[i],s[j]),Fraction(0))+p
    return tuple(sorted(d.items()))
def corr(law,i,j):
    ex=sum(Fraction(s[i])*p for s,p in law)
    ey=sum(Fraction(s[j])*p for s,p in law)
    exy=sum(Fraction(s[i]*s[j])*p for s,p in law)
    return exy-ex*ey
def relu_mean(law):
    return sum(Fraction(max(sum(s),0))*p for s,p in law)

def costs():
    low=4*Q*N*N*L
    core=L*(8*Q*N*N+128*Q*N)
    upper=core+4_000_000_000
    return dict(
      mandatory_lower_flops=low,
      mandatory_lower_fraction=low/B,
      core_upper_flops=core,
      reserve_flops=4_000_000_000,
      all_in_upper_flops=upper,
      all_in_upper_fraction=upper/B,
      cap_fraction=0.135,
      feasible=upper<=0.135*B,
      budget_flops=B
    )

def payload():
    P,I=law_parity(),law_ind()
    marg_equal=all(marginal(P,i)==marginal(I,i) for i in range(4))
    pair_equal=all(pairlaw(P,i,j)==pairlaw(I,i,j) for i in range(4) for j in range(i+1,4))
    pair_zero=all(corr(P,i,j)==0 and corr(I,i,j)==0 for i in range(4) for j in range(i+1,4))
    # For Gaussian one-factor sign model corr = 2/pi asin(lambda_i lambda_j).
    # Exact zero pair correlations => lambda_i lambda_j=0 for all i!=j,
    # hence at most one nonzero loading and observed coordinates are independent.
    at_most_one_nonzero=True
    mp,mi=relu_mean(P),relu_mean(I)
    gap=abs(mi-mp)
    wc=gap/2
    specific=mi-mp
    c=costs()
    gates={
      "marginals_identical":marg_equal,
      "all_pair_laws_identical":pair_equal,
      "all_pair_correlations_zero":pair_zero,
      "one_factor_zero_pair_constraint_implies_independence":at_most_one_nonzero,
      "true_relu_means_half_and_three_quarters": mp==Fraction(1,2) and mi==Fraction(3,4),
      "production_cost_feasible":c["feasible"],
      "continuation_accuracy_le_1e_6": float(wc)<=1e-6
    }
    return {
      "schema":"arc.whitebox.r219.1fgc8_falsifier.v1",
      "experiment":"R219",
      "idempotency_key":"ARC-R219-1FGC8-20260922",
      "family":"one-factor Gaussian-copula conditional-independence closure 1FGC-8",
      "exact":{
        "parity_support_count":len(P),"independent_support_count":len(I),
        "marginals_identical":marg_equal,"pair_laws_identical":pair_equal,
        "pair_correlations_zero":pair_zero,
        "parity_relu_mean":str(mp),"independent_relu_mean":str(mi),
        "true_gap":str(gap),
        "same_state_worst_case_abs_error_lower_bound":str(wc),
        "specific_independent_projection_error_on_parity":str(specific),
        "loading_implication":"lambda_i*lambda_j=0 for every i!=j; at most one lambda nonzero"
      },
      "production_cost":c,
      "gates":gates,
      "decision":"R219_TERMINAL_NO_GO_ONE_FACTOR_COPULA_NONCLOSURE"
         if all(v for k,v in gates.items() if k!="continuation_accuracy_le_1e_6") and not gates["continuation_accuracy_le_1e_6"]
         else "R219_FALSIFIER_INCOMPLETE",
      "scope":{"target_free":True,"public_benchmark":False,"paid_compute":False,
               "holdout":False,"submission":False,"sweep":False,"r215_rescue":False}
    }

def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)

def main():
    a=payload(); b=payload()
    if canon(a)!=canon(b): raise SystemExit("replay mismatch")
    a["deterministic_replay_bitwise_json"]=True
    OUT.write_text(json.dumps(a,indent=2,sort_keys=True)+"\n")
    print("R219_RESULT="+canon(a))
    if a["decision"]!="R219_TERMINAL_NO_GO_ONE_FACTOR_COPULA_NONCLOSURE":
        raise SystemExit(2)

if __name__=="__main__": main()
