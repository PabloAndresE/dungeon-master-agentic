import json, re, glob, pandas as pd, sys
SIS=['Baseline','Agente v1','Multi v2']
def lote(d, tag):
    rows=[]; turnos=[]; faith=[]
    for i in (1,2,3):
        try: nb=json.load(open(f'{d}/v2_run{i}.ipynb'))
        except FileNotFoundError: continue
        errs=[(c.get('id'),o['ename']) for c in nb['cells'] for o in c.get('outputs',[]) if o.get('output_type')=='error']
        out={c.get('id'):''.join(''.join(o.get('text','')) for o in c.get('outputs',[])) for c in nb['cells'] if c['cell_type']=='code'}
        kw=dict(re.findall(r"(Baseline|Agente v1|Multi v2):\s+(\d+)/\d+",out['eval-kw-v2']))
        exp=re.search(r"Expansiones del mundo: (\d+)",out['run-v2']).group(1)
        df=pd.read_csv(f'{d}/juez_por_turno_{tag}{i}.csv'); p=df[df.juez=='72B']
        g=p.groupby('sistema')[['consistencia','reglas','narrativa','final']].mean()
        srd=p[p.field=='srd'].groupby('sistema').final.mean()
        f=pd.read_csv(f'{d}/faithfulness_{tag}{i}.csv'); faith.append(f.assign(run=i))
        for s in SIS:
            rows.append(dict(run=i,sistema=s,**g.loc[s].round(1).to_dict(),juez_srd=round(srd[s],1),
                             faith_srd=round(f[(f.sistema==s)&(f.field=='srd')].faithfulness.mean(),2),
                             faith_resumen=round(f[(f.sistema==s)&(f.field=='event_memory')].faithfulness.mean(),2),
                             kw=int(kw.get(s,0)),exp=exp,errs=len(errs)))
        turnos.append(p.pivot_table(index=['turno','field'],columns='sistema',values='final'))
    R=pd.DataFrame(rows)
    return R, sum(turnos)/len(turnos), pd.concat(faith)
for d,tag in [(a,b) for a,b in [(x.split(':')[0],x.split(':')[1]) for x in (sys.argv[1:] or ['runs_holdout:holdout','runs_corregido:corregido'])]]:
    R,T,F=lote(d,tag)
    print(f'\n=========== {d} ({R.run.nunique()} corridas)'); print(R.to_string())
    print(R.groupby('sistema')[['consistencia','reglas','narrativa','final','juez_srd','faith_srd','faith_resumen','kw']].agg(['mean','std']).round(2).loc[SIS].to_string())
    print(T.round(0)[SIS].to_string())
