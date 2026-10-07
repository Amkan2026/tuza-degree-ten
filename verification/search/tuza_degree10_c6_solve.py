import itertools,time
from ortools.sat.python import cp_model

def variables(r,first):
    return [(c,first+j) for j in range(r) for c in range(6)]+list(itertools.combinations(range(first,first+r),2))

def graph(H,sa,sb,p,q):
    A=list(range(8,8+sa));B=list(range(11,11+sb))
    E={tuple(e) for e in H}|{(c,6) for c in range(6)}|{(c,7) for c in range(6)}|{(6,7)}|{(6,a) for a in A}|{(7,b) for b in B}
    E|={e for i,e in enumerate(variables(sa,8)) if p>>i&1}
    E|={e for i,e in enumerate(variables(sb,11)) if q>>i&1}
    return sorted(E),A,B

def triangles(E):
    ed={e:i for i,e in enumerate(E)}
    return [(t,[ed[e] for e in itertools.combinations(t,2)]) for t in itertools.combinations(range(14),3) if all(e in ed for e in itertools.combinations(t,2))]

def pair(H,sa,sb,p,q,fixed=True,tlim=2,spare=0):
    started=time.time()
    E,A,B=graph(H,sa,sb,p,q);ed={e:i for i,e in enumerate(E)};T=triangles(E)
    model=cp_model.CpModel()
    x=[model.new_bool_var(f'x{i}') for i in range(len(E))]
    y=[model.new_bool_var(f't{i}') for i in range(len(T))]
    if fixed:
        for a in A:model.add(x[ed[6,a]]==1)
        for b in B:model.add(x[ed[7,b]]==1)
    inc=[[] for e in E]
    for j,(t,te) in enumerate(T):
        for e in te:inc[e].append(y[j])
        if 6 in t or 7 in t:model.add(sum(x[e] for e in te)>=1)
    for i,e in enumerate(E):
        model.add(sum(inc[i])<=1)
        if 6 not in e and 7 not in e:model.add(sum(inc[i])<=x[i])
    model.add(sum(x)+spare<=2*sum(y))
    s=cp_model.CpSolver();s.parameters.max_time_in_seconds=tlim;s.parameters.num_search_workers=2
    status=s.solve(model)
    if status not in [cp_model.OPTIMAL,cp_model.FEASIBLE]:return {'status':s.status_name(status),'seconds':time.time()-started}
    return {'status':'PASS','kind':'pair','fixed_spokes':fixed,'U':[6,7],'X':[e for i,e in enumerate(E) if s.value(x[i])],'S':[t for i,(t,_) in enumerate(T) if s.value(y[i])],'seconds':time.time()-started}

def cut(H,sa,sb,p,q,tlim=10,monotone=False):
    started=time.time()
    E,A,B=graph(H,sa,sb,p,q);T=triangles(E)
    deficit=[10-sum(c in e for e in E) for c in range(6)]
    if min(deficit)<0:return {'status':'LOCAL_DEGREE_EXCEEDS_TEN'}
    m=cp_model.CpModel();c=[m.new_bool_var(f'c{i}') for i in range(14)]
    for a in A:m.add(c[a]==0)
    for b in B:m.add(c[b]==1)
    x=[m.new_bool_var(f'x{i}') for i in range(len(E))]
    for i,(a,b) in enumerate(E):m.add_allowed_assignments([c[a],c[b],x[i]],[(0,0,1),(1,1,1),(0,1,0),(1,0,0)])
    z=[m.new_bool_var(f'z{i}') for i in range(6)]
    if monotone=='full':
        for zz in z:m.add(zz==1)
    y=[m.new_bool_var(f't{i}') for i in range(len(T))];inc=[[] for e in E]
    for j,(t,te) in enumerate(T):
        for e in te:
            inc[e].append(y[j]);a,b=E[e]
            if 6 not in (a,b) and 7 not in (a,b):m.add(y[j]<=x[e]+sum(z[v] for v in (a,b) if v<6))
    for cc in inc:m.add(sum(cc)<=1)
    extra=0
    weighted=[]
    if monotone:
        extra=sum(e not in E for W in [A,B] for e in itertools.combinations(W,2))
        if monotone=='bounded':
            for i in range(6):
                d=sum(i in e for e in H)
                aa=sum((i,a) in E for a in A)
                bb=sum((i,b) in E for b in B)
                ea=min(sa,5-d)-aa
                eb=min(sb,5-d)-bb
                assert min(ea,eb)>=0
                wa=m.new_bool_var(f'wa{i}');wb=m.new_bool_var(f'wb{i}')
                m.add_allowed_assignments([z[i],c[i],wa,wb],[(0,0,1,0),(0,1,0,1),(1,0,0,0),(1,1,0,0)])
                weighted.extend([ea*wa,eb*wb])
    m.add(sum(x)+sum(deficit[i]*z[i] for i in range(6))+extra+sum(weighted)<=2*sum(y))
    s=cp_model.CpSolver();s.parameters.max_time_in_seconds=tlim;s.parameters.num_search_workers=2
    status=s.solve(m)
    if status not in [cp_model.OPTIMAL,cp_model.FEASIBLE]:return {'status':s.status_name(status),'seconds':time.time()-started}
    Z=[v for v in range(6) if s.value(z[v])];colors=[s.value(v) for v in c]
    X=[e for i,e in enumerate(E) if s.value(x[i])];S=[t for i,(t,_) in enumerate(T) if s.value(y[i])]
    outside=sum(deficit[v] for v in Z)
    contact_extra=0
    if monotone=='bounded':
        for i in range(6):
            if i in Z:continue
            d=sum(i in e for e in H)
            W=A if colors[i]==0 else B
            contact_extra+=min(len(W),5-d)-sum((i,a) in E for a in W)
    return {'status':'PASS','kind':'monotone_cut' if monotone else 'subset_cut','monotone_mode':monotone,'U':Z+[6,7],'colors':colors,'X':X,'S':S,'outside_bound':outside,'additional_internal_budget':extra,'additional_contact_budget':contact_extra,'total_cover_bound':len(X)+outside+extra+contact_extra,'seconds':time.time()-started}

def general(H,sa,sb,p,q,tlim=10,monotone=True):
                                                                                 

                                                                              
                                                                           
       
    started=time.time()
    E,A,B=graph(H,sa,sb,p,q);T=triangles(E);ed={e:i for i,e in enumerate(E)}
    V=list(range(6))+A+B
    deficit={v:10-sum(v in e for e in E) for v in V}
    assert min(deficit.values(),default=0)>=0
    m=cp_model.CpModel()
    z={v:m.new_bool_var(f'z{v}') for v in V}
    x=[m.new_bool_var(f'x{i}') for i in range(len(E))]
    y=[m.new_bool_var(f't{i}') for i in range(len(T))]
    cross={(a,b):m.new_bool_var(f'cross{a}_{b}') for a in A for b in B}
    inc=[[] for e in E]
    for j,(t,te) in enumerate(T):
        for ei in te:
            inc[ei].append(y[j]);a,b=E[ei]
            if 6 not in (a,b) and 7 not in (a,b):m.add(y[j]<=x[ei]+z[a]+z[b])
        if 6 in t or 7 in t:m.add(sum(x[ei] for ei in te)>=1)
        else:
            for v in t:m.add(sum(x[ei] for ei in te)>=z[v])
    for ii in inc:m.add(sum(ii)<=1)
    for c in range(6):
        for a in A:
            if (c,a) not in ed:continue
            for b in B:
                if (c,b) in ed:m.add(x[ed[c,a]]+x[ed[c,b]]+cross[a,b]+z[a]+z[b]>=z[c])
    extras=[]
    if monotone:
        for W in [A,B]:
            for a,b in itertools.combinations(W,2):
                if (a,b) in ed:continue
                w=m.new_bool_var(f'add{a}_{b}')
                m.add_allowed_assignments([z[a],z[b],w],[(0,0,1),(0,1,0),(1,0,0),(1,1,0)])
                extras.append(w)
        for c in range(6):
            d=sum(c in e for e in H)
            for si,W in enumerate([A,B]):
                present=sum((c,a) in ed for a in W)
                cap=min(len(W),5-d)-present
                assert cap>=0
                missing=[a for a in W if (c,a) not in ed]
                slots=m.new_int_var(0,len(W),f'slots{c}_{si}')
                m.add(slots==sum(1-z[a] for a in missing))
                bound=m.new_int_var(0,len(W),f'bound{c}_{si}')
                m.add_min_equality(bound,[slots,cap])
                charge=m.new_int_var(0,len(W),f'charge{c}_{si}')
                m.add(charge==bound).only_enforce_if(z[c].Not())
                m.add(charge==0).only_enforce_if(z[c])
                extras.append(charge)
    m.add(sum(x)+sum(deficit[v]*z[v] for v in V)+sum(cross.values())+sum(extras)<=2*sum(y))
    s=cp_model.CpSolver();s.parameters.max_time_in_seconds=tlim;s.parameters.num_search_workers=2
    status=s.solve(m)
    if status not in [cp_model.OPTIMAL,cp_model.FEASIBLE]:return {'status':s.status_name(status),'seconds':time.time()-started}
    Z=[v for v in V if s.value(z[v])]
    X=[e for i,e in enumerate(E) if s.value(x[i])]
    S=[t for i,(t,_) in enumerate(T) if s.value(y[i])]
    AB=[e for e,v in cross.items() if s.value(v)]
    out=sum(deficit[v] for v in Z);extra=sum(s.value(v) for v in extras)
    return {'status':'PASS','kind':'monotone_general' if monotone else 'general','U':sorted(Z+[6,7]),'X':X,'S':S,'conditional_cross_cover':AB,'outside_bound':out,'additional_variable_budget':extra,'total_cover_bound':len(X)+out+len(AB)+extra,'seconds':time.time()-started}
