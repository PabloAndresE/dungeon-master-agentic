exec(open("/root/dungeon-master-agentic/pruebas/harness.py").read())
import re, json, sys
exec(open("/root/dungeon-master-agentic/holdout3_seq.py").read(), g); exec(compile("".join(next(c for c in nb["cells"] if c.get("id")=="test-seq-v2")["source"]),"seq","exec"), g)
g["reset_game"](); dm = g["MultiAgentDM"](g["app_v2"]); out=[]
for i,(a,q,f,e) in enumerate(g[sys.argv[2]]):
    ra = dm.play(a); intent_a = g["INTENCION"]["tipo"]; rq = dm.play(q)
    out.append(dict(t=i+1,a=a,q=q,ra=ra,rq=rq,int_a=intent_a,loc=g["game_state"]["location"]))
    print(f"t{i+1} [{intent_a}] {a}\n  → {ra[:260]!r}\n  ? {q} → {rq[:200]!r}", flush=True)
json.dump(out, open(sys.argv[1],"w"), ensure_ascii=False, indent=1)
