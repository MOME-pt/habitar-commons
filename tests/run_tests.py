#!/usr/bin/env python3
"""Corre os testes do ruleset: cada regra tem pelo menos um caso que deve disparar e outro que deve passar."""
import copy, json, sys
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "validator"))
from validate import validate

def setp(d, path, v):
    *ps, k = path.split(".")
    for p in ps: d = d.setdefault(p, {})
    d[k] = v

def delp(d, path):
    *ps, k = path.split(".")
    for p in ps: d = d.get(p, {})
    d.pop(k, None)

rules = yaml.safe_load((ROOT / "spec/rules_v1_3_1.yaml").read_text())
schema = json.loads((ROOT / "spec/manifest.schema.json").read_text())
base = yaml.safe_load((ROOT / "tests/base_project.yaml").read_text())
cases = yaml.safe_load((ROOT / "tests/cases.yaml").read_text())
fails = 0

f0 = [f for f in validate(base, rules, schema) if f[0] != "info"]
print(("OK  " if not f0 else "FAIL") + " base_project: sem erros nem avisos" + ("" if not f0 else f" -> {f0}"))
fails += bool(f0)
tpl = yaml.safe_load((ROOT / "examples/HC-CR-MID_v1_3_1.yaml").read_text())
ft = [f for f in validate(tpl, rules, schema) if f[0] != "info"]
print(("OK  " if not ft else "FAIL") + " HC-CR-MID v1.3.1: sem erros nem avisos" + ("" if not ft else f" -> {ft}"))
fails += bool(ft)

covered = {}
for c in cases:
    m = copy.deepcopy(base)
    for p, v in (c.get("set") or {}).items(): setp(m, p, v)
    for p in c.get("del") or []: delp(m, p)
    out = validate(m, rules, schema)
    sch = [f for f in out if f[1] == "SCH"]
    fired = any(f[1] == c["rule"] for f in out)
    ok = (fired == (c["expect"] == "fires")) and not sch
    covered.setdefault(c["rule"], set()).add(c["expect"])
    fails += not ok
    tag = f" ({c['note']})" if c.get("note") else ""
    print(f"{'OK  ' if ok else 'FAIL'} {c['rule']:6} {c['expect']:6}{tag}" + ("" if ok else f" -> {out}"))

missing = [r["id"] for r in rules["rules"] if covered.get(r["id"]) != {"fires", "passes"}]
if missing:
    print("FAIL regras sem os dois casos:", missing); fails += 1
print(f"\n{len(cases)} casos, {fails} falha(s)")
sys.exit(1 if fails else 0)
