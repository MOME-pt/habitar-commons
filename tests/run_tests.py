#!/usr/bin/env python3
"""Corre os testes do ruleset v2.0-rc1: cada regra tem um caso que deve disparar e outro que deve passar.
Verifica também o manifesto-base, o modelo HC-CR-MID e os casos de representação."""
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

rules = yaml.safe_load((ROOT / "spec/rules_v2_0.yaml").read_text(encoding="utf-8"))
schema = json.loads((ROOT / "spec/manifest.schema.json").read_text(encoding="utf-8"))
base = yaml.safe_load((ROOT / "tests/base_project.yaml").read_text(encoding="utf-8"))
fails = 0

def check(label, m, ok_if):
    global fails
    out = validate(m, rules, schema)
    ok = ok_if(out)
    fails += not ok
    print(f"{'OK  ' if ok else 'FAIL'} {label}" + ("" if ok else f" -> {[f for f in out if f[0] != 'info']}"))

check("base_project: sem erros nem avisos", base, lambda o: not [f for f in o if f[0] != "info"])
tpl = yaml.safe_load((ROOT / "examples/HC-CR-MID_v2_0.yaml").read_text(encoding="utf-8"))
check("HC-CR-MID v2.0-rc1: sem erros nem avisos", tpl, lambda o: not [f for f in o if f[0] != "info"])

covered = {}
for c in yaml.safe_load((ROOT / "tests/cases.yaml").read_text(encoding="utf-8")):
    m = copy.deepcopy(base)
    for p, v in (c.get("set") or {}).items(): setp(m, p, v)
    for p in c.get("del") or []: delp(m, p)
    out = validate(m, rules, schema)
    sch = [f for f in out if f[1] == "SCH"]
    fired = any(f[1] == c["rule"] and f[2] != "não verificada: depende de campos privados da Camada 6" for f in out)
    others = [f for f in out if f[0] in ("error", "warning") and f[1] != c["rule"] and f[1] not in (c.get("also") or [])]
    ok = (fired == (c["expect"] == "fires")) and not sch and not others
    covered.setdefault(c["rule"], set()).add(c["expect"])
    fails += not ok
    tag = f" ({c['note']})" if c.get("note") else ""
    print(f"{'OK  ' if ok else 'FAIL'} {c['rule']:6} {c['expect']:6}{tag}" + ("" if ok else f" -> {[f for f in out if f[0] != 'info' or f[1]==c['rule']]}"))

missing = [r["id"] for r in rules["rules"] if covered.get(r["id"]) != {"fires", "passes"}]
if missing:
    print("FAIL regras sem os dois casos:", missing); fails += 1

# casos de representação (separador 13): cada manifesto em tests/representation/ declara o resultado esperado
rep = sorted((ROOT / "tests/representation").glob("*.yaml"))
for f in rep:
    m = yaml.safe_load(f.read_text(encoding="utf-8"))
    exp = m.pop("expect")
    out = validate(m, rules, schema)
    got = sorted({x[1] for x in out if x[0] in ("error", "warning")})
    ok = got == sorted(exp)
    fails += not ok
    print(f"{'OK  ' if ok else 'FAIL'} representação {f.stem}: esperado {sorted(exp)}" + ("" if ok else f", obtido {got} {out}"))
n = len(yaml.safe_load((ROOT / 'tests/cases.yaml').read_text(encoding='utf-8')))
print(f"\n{n} casos de regra, {len(rep)} casos de representação, {fails} falha(s)")
sys.exit(1 if fails else 0)
