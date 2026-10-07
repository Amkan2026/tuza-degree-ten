                                                                         
from ortools.sat.python import cp_model
from tuza_degree10_c6_solve import graph,triangles,variables
import time

def pair_wide(H,sa,sb,p,q,tlim=3,fixed=False):
    start=time.time();E,A,B=graph(H,sa,sb,p,q);ed={e:i for i,e in enumerate(E)};T=triangles(E)
    m=cp_model.CpModel();x=[m.new_bool_var(f'x{i}') for i in range(len(E))];y=[m.new_bool_var(f'y{i}') for i in range(len(T))]
    inc=[[] for e in E]
    for j,(t,te) in enumerate(T):
        for e in te:inc[e].append(y[j])
        if 6 in t or 7 in t:m.add(sum(x[e] for e in te)>=1)
    for i,e in enumerate(E):
        m.add(sum(inc[i])<=1)
        if 6 not in e and 7 not in e:m.add(sum(inc[i])<=x[i])
    if fixed:
        for a in A:m.add(x[ed[6,a]]==1)
        for b in B:m.add(x[ed[7,b]]==1)
    m.add(sum(x)<=2*sum(y))
    required=[];forbidden=[]
    for r,first,hub in [(sa,8,6),(sb,11,7)]:
        for e in variables(r,first):
            if e in ed:required.extend(inc[ed[e]])
            a,b=e;f=m.new_bool_var(f'f{len(forbidden)}');forbidden.append(f)
            xe=x[ed[e]] if e in ed else 0
            xa=x[ed[tuple(sorted((hub,a)))]];xb=x[ed[tuple(sorted((hub,b)))]]
            m.add(f>=1-xe-xa-xb)
    m.minimize(100*(sum(required)+sum(forbidden))+sum(x)+sum(y))
    s=cp_model.CpSolver();s.parameters.max_time_in_seconds=tlim;s.parameters.num_search_workers=2
    status=s.solve(m)
    if status not in [cp_model.OPTIMAL,cp_model.FEASIBLE]:return {'status':s.status_name(status),'seconds':time.time()-start}
    return {'status':'PASS','kind':'pair','fixed_spokes':fixed,'wide_objective':True,'objective_value':s.objective_value,'U':[6,7],'X':[e for i,e in enumerate(E) if s.value(x[i])],'S':[t for i,(t,_) in enumerate(T) if s.value(y[i])],'seconds':time.time()-start}
