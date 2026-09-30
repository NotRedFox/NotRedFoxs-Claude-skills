import importlib.util, random, sys
PATHS={"A":"contenders/A_sliding_log.py","C":"contenders/C_ring_buffer.py","D":"contenders/D_bucketed_window.py","F":"limiter.py"}
def load(c):
    s=importlib.util.spec_from_file_location("lim_"+c,PATHS[c]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
mods={c:load(c) for c in "ACDF"}
def oracle_ok(hist,limit,window,now,cost):
    # would admitting cost at now break R1? check every interval ending at or after now containing now
    used=sum(c for t,c in hist if t>now-window)
    return used+cost<=limit
diff={c:0 for c in mods}; ex={}
rng=random.Random(7)
for trial in range(3000):
    limit=rng.randint(1,8); window=rng.choice([1.0,10.0,60.0])
    lims={c:m.RateLimiter({"p":(limit,window)}) for c,m in mods.items()}
    hist=[]; now=0.0
    for step in range(40):
        now+=rng.choice([0,0,rng.random()*window/20,rng.random()*window/3,rng.random()*window])
        cost=rng.randint(1,limit)
        ok=oracle_ok(hist,limit,window,now,cost)
        for c,l in lims.items():
            d=l.allow("k","p",now,cost)
            if d.allowed!=ok:
                diff[c]+=1; ex.setdefault(c,(limit,window,list(hist),now,cost,d.allowed,ok))
        if ok: hist.append((now,cost))
print("mismatches vs brute-force oracle:",diff)
for c,e in ex.items(): print(c,"first mismatch: limit=%d window=%s now=%.4f cost=%d got=%s expected=%s last_hist=%s"%(e[0],e[1],e[3],e[4],e[5],e[6],e[2][-4:]))
