from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'axes.spines.top':False, 'axes.spines.right':False,
                     'figure.dpi':150, 'axes.titleweight':'bold'})
(ROOT/'figures').mkdir(exist_ok=True)

import json
import numpy as np
from execution_dp import exact_dp,simulate_schedule
result=exact_dp(200,5,alpha=.08,pi=.5,max_states=200000)
equal=[40]*5
equal_fills,_=simulate_schedule(equal,alpha=.08,pi=.5)
fig,axes=plt.subplots(1,2,figsize=(10,3.7),layout='constrained')
period=np.arange(1,6)
axes[0].bar(period-.18,result['schedule'],width=.36,label='Exact DP',color='#157a83')
axes[0].bar(period+.18,equal,width=.36,label='Equal-sized',color='#d69b3a')
axes[0].set(xlabel='Execution period',ylabel='Ordered shares',title='Synthetic schedule comparison')
axes[0].legend()
axes[1].plot(range(1,5),result['raw_state_counts'],'o-',label='Before pruning',color='#d69b3a')
axes[1].plot(range(1,5),result['state_counts'],'o-',label='Nondominated',color='#157a83')
axes[1].set(xlabel='DP expansion',ylabel='Reachable states',title='Dominance pruning')
axes[1].legend()
fig.savefig(ROOT/'figures/execution-study.svg')
summary={k:list(v) if isinstance(v,tuple) else v.tolist() if isinstance(v,np.ndarray) else v for k,v in result.items()}
summary['equal_fills']=int(equal_fills.sum())
(ROOT/'figures/results.json').write_text(json.dumps(summary,indent=2))
print('Exact fills:',result['total'],'equal fills:',int(equal_fills.sum()))
