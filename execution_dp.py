"""Solvers extracted from the trade-scheduling coursework notebook."""
import math
import numpy as np
ALPHA, PI = 0.001, 0.5

def memory_after(previous_memory, order):
    return (int(previous_memory) + int(order) + 1) // 2

def fill_count(memory, order, alpha=ALPHA, pi=PI):
    return int(math.ceil(max(0.0, 1.0-alpha*(memory**pi))*order))

def simulate_schedule(schedule, alpha=ALPHA, pi=PI):
    memory=0; fills=[]; memories=[]
    for n in map(int,schedule):
        memory=memory_after(memory,n); memories.append(memory); fills.append(fill_count(memory,n,alpha,pi))
    return np.array(fills,dtype=int), np.array(memories,dtype=int)

def exact_fill_count(memory, order):
    # For N <= 100000, alpha*sqrt(memory) < 1.  Therefore
    # ceil((1 - sqrt(memory)/1000)*order)
    # = order - floor(order*sqrt(memory)/1000).
    # isqrt(order**2 * memory) gives floor(order*sqrt(memory)) exactly.
    order=int(order); memory=int(memory)
    loss=math.isqrt(order*order*memory)//1000
    return max(0, order-loss)

def approximate_dp(N,T,alpha=ALPHA,pi=PI,order_step=1000):
    units=N//order_step; states={(0,0):(0,())}; counts=[]
    for _ in range(T-1):
        nxt={}
        for (planned,memory),(value,path) in states.items():
            for du in range(units-planned+1):
                n=du*order_step; m2=memory_after(memory,n); v2=value+fill_count(m2,n,alpha,pi)
                key=(planned+du,m2); old=nxt.get(key)
                if old is None or v2>old[0]: nxt[key]=(v2,path+(n,))
        states=nxt; counts.append(len(states))
    best=(-1,None)
    for (planned,memory),(value,path) in states.items():
        n=N-planned*order_step; m2=memory_after(memory,n); total=value+fill_count(m2,n,alpha,pi)
        if total>best[0]: best=(total,path+(n,))
    fills,memories=simulate_schedule(best[1],alpha,pi)
    return {'schedule':best[1],'fills':fills,'memories':memories,'total':int(best[0]),'state_counts':counts}

def exact_dp(N,T,alpha=ALPHA,pi=PI, max_states=None):
    """Exact integer DP with dominance pruning over reachable states.

    State is (planned shares, current memory). For each planned amount x,
    a state (x,m1,v1) dominates (x,m2,v2) when m1 <= m2 and v1 >= v2.
    Since future memory is monotone in current memory and future fills are
    nonincreasing in memory, dominated states can never lead to a better
    completion. No order or memory grid is used; every integer action is
    considered before pruning.
    """
    states={(0,0):(0,())}; raw_counts=[]; kept_counts=[]
    integer_default_model=(abs(alpha-0.001)<1e-15 and abs(pi-0.5)<1e-15)
    reward=lambda memory,order: exact_fill_count(memory,order) if integer_default_model else fill_count(memory,order,alpha,pi)
    for period in range(T-1):
        raw={}
        for (planned,memory),(value,path) in states.items():
            for n in range(N-planned+1):
                m2=memory_after(memory,n); v2=value+reward(m2,n)
                key=(planned+n,m2); old=raw.get(key)
                if old is None or v2>old[0]: raw[key]=(v2,path+(n,))
        raw_counts.append(len(raw))
        by_planned={}
        for (planned,memory),(value,path) in raw.items():
            by_planned.setdefault(planned,[]).append((memory,value,path))
        states={}
        for planned,frontier in by_planned.items():
            best_value=-1
            for memory,value,path in sorted(frontier):
                if value>best_value:
                    states[(planned,memory)]=(value,path); best_value=value
        kept_counts.append(len(states))
        if max_states is not None and len(states)>max_states:
            raise MemoryError(f'period {period+1}: {len(states):,} nondominated states > cap {max_states:,}')
    best=(-1,None)
    for (planned,memory),(value,path) in states.items():
        n=N-planned; m2=memory_after(memory,n); total=value+reward(m2,n)
        if total>best[0]: best=(total,path+(n,))
    fills,memories=simulate_schedule(best[1],alpha,pi)
    return {'schedule':best[1],'fills':fills,'memories':memories,'total':int(best[0]),
            'raw_state_counts':raw_counts,'state_counts':kept_counts}

def brute_force(N,T,alpha=ALPHA,pi=PI):
    best=(-1,None)
    def rec(prefix,remaining,slots):
        nonlocal best
        if slots==1:
            s=tuple(prefix+[remaining])
            memory=0; val=0
            for n in s:
                memory=memory_after(memory,n)
                val += exact_fill_count(memory,n) if abs(alpha-0.001)<1e-15 and abs(pi-0.5)<1e-15 else fill_count(memory,n,alpha,pi)
            if val>best[0]: best=(val,s)
        else:
            for n in range(remaining+1): rec(prefix+[n],remaining-n,slots-1)
    rec([],N,T); return best
