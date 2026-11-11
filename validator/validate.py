#!/usr/bin/env python3
"""Habitar Commons — validador de referência (v1.3.1).

Uso:  python validator/validate.py <manifesto.yaml> [--rules spec/rules_v1_3_1.yaml]

Verifica, por esta ordem:
  1. o esquema (spec/manifest.schema.json): campos, tipos e cardinalidade;
  2. sinónimos obsoletos (kind: license, campo license);
  3. as regras do ruleset.

Licença: CC BY-SA 4.0. Francisco Rocha Antunes, Filipa Serôdio Pinheiro · MOME, Porto.
O validador verifica a coerência interna do manifesto. Não verifica a conformidade
jurídica nem a correspondência com estatutos, contratos ou outros documentos.
"""
import json, re, sys, argparse
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
MISSING = object()
PLACEHOLDER_KEYS = {"type", "description", "unit", "required_if"}

# ── caminhos ────────────────────────────────────────────────────────────────
TOKEN = re.compile(r"([^.\[\]]+)(\[(\*|[a-z_]+=[^\]]+)\])?")

def resolve(doc, path):
    """Devolve o valor no caminho, ou MISSING. Suporta a.b, lista[*].campo e lista[id=X].campo."""
    cur = [doc]
    multi = False
    for name, _, sel in TOKEN.findall(path):
        nxt = []
        for node in cur:
            if isinstance(node, dict) and name in node:
                nxt.append(node[name])
        if not nxt:
            return MISSING
        if sel:
            out = []
            for node in nxt:
                if not isinstance(node, list):
                    continue
                if sel == "*":
                    out.extend(node); multi = True
                else:
                    k, v = sel.split("=", 1)
                    out.extend(i for i in node if isinstance(i, dict) and str(i.get(k)) == v)
            if not out:
                return MISSING if sel != "*" else []
            nxt = out
        cur = nxt
    if multi:
        return cur
    return cur[0] if cur else MISSING

def has_value(v):
    if v is MISSING or v is None:
        return False
    if isinstance(v, str):
        return v.strip() != ""
    if isinstance(v, (list, tuple)):
        return len(v) > 0
    if isinstance(v, dict):
        if not v:
            return False
        if set(v.keys()) <= PLACEHOLDER_KEYS:   # objeto de esquema, não um valor
            return False
        if "value" in v:
            return has_value(v["value"])
        return True
    return True

# ── condições ───────────────────────────────────────────────────────────────
class Ctx:
    def __init__(self, manifest, ruleset):
        self.doc = dict(manifest)
        self.doc.setdefault("catalog", ruleset.get("catalog", {}))
        self.template = manifest.get("kind") in ("template", "license")
        self.pending = []          # has_value falhados em modelos

def value_of(ctx, v):
    if isinstance(v, dict) and set(v) == {"ref"}:
        return resolve(ctx.doc, v["ref"])
    return v

def as_list(v):
    return v if isinstance(v, list) else [v]

def test(ctx, cond):
    if "all" in cond:
        return all(test(ctx, c) for c in cond["all"])
    if "any" in cond:
        return any(test(ctx, c) for c in cond["any"])
    if "not" in cond:
        return not test(ctx, cond["not"])
    op, path = cond["op"], cond["path"]
    v = resolve(ctx.doc, path)
    target = value_of(ctx, cond.get("value"))
    if op == "exists":
        return v is not MISSING
    if op == "has_value":
        ok = has_value(v)
        if not ok and ctx.template and v is not MISSING:
            ctx.pending.append(path)
            return True
        return ok
    if v is MISSING or target is MISSING:
        return False
    if op in ("eq", "ne", "in", "not_in"):
        if isinstance(v, list):
            raise TypeError(f"operador de escalar '{op}' aplicado à lista em {path}")
        return {"eq": v == target, "ne": v != target,
                "in": v in as_list(target), "not_in": v not in as_list(target)}[op]
    if op in ("contains", "contains_any", "contains_all", "contains_none", "subset_of"):
        if not isinstance(v, list):
            raise TypeError(f"operador de lista '{op}' aplicado ao escalar em {path}")
        t = as_list(target)
        return {"contains": target in v,
                "contains_any": any(x in v for x in t),
                "contains_all": all(x in v for x in t),
                "contains_none": not any(x in v for x in t),
                "subset_of": all(x in t for x in v)}[op]
    if op == "sum_eq":
        return abs(sum(as_list(v)) - float(target)) < 1e-3
    raise ValueError(f"operador desconhecido: {op}")

# ── validação ───────────────────────────────────────────────────────────────
def validate(manifest, ruleset, schema=None):
    findings = []   # (nível, id, mensagem)
    if schema is not None:
        try:
            import jsonschema
            v = jsonschema.Draft202012Validator(schema)
            for e in sorted(v.iter_errors(manifest), key=lambda e: list(e.path)):
                loc = ".".join(str(p) for p in e.path) or "(raiz)"
                findings.append(("error", "SCH", f"{loc}: {e.message}"))
        except ImportError:
            findings.append(("info", "SCH", "jsonschema não instalado: esquema não verificado"))
    if manifest.get("kind") == "license":
        findings.append(("warning", "DEP001", "kind: license está obsoleto; usar kind: template"))
    if "license" in manifest and "spec_license" not in manifest:
        findings.append(("warning", "DEP002", "o campo license está obsoleto; usar spec_license"))
    manifest = normalize(manifest, findings)
    juris = set(manifest.get("jurisdiction", []))
    ctx = Ctx(manifest, ruleset)
    for r in ruleset["rules"]:
        if r.get("jurisdiction") and not juris & set(r["jurisdiction"]):
            continue
        try:
            fires = test(ctx, r["when"]) and ("then" not in r or not test(ctx, r["then"]))
        except TypeError as e:
            findings.append(("error", r["id"], f"regra mal aplicada ao esquema: {e}"))
            continue
        if fires:
            findings.append((r["severity"], r["id"], r["message"]))
    for p in dict.fromkeys(ctx.pending):
        findings.append(("info", "TPL", f"a preencher por projeto: {p}"))
    return findings

LIST_FIELDS = ["axes.economics", "axes.finance", "axes.governance", "axes.safeguards",
               "axes.revision", "axes.population", "overlays", "modules.use", "modules.mobility",
               "modules.improvements", "modules.intermediation", "operation.developer",
               "operation.allocator"]

def normalize(manifest, findings):
    """Converte em lista os eixos multivalor declarados como código isolado (compatibilidade v1.3)."""
    import copy
    m = copy.deepcopy(manifest)
    for path in LIST_FIELDS:
        *parents, leaf = path.split(".")
        node = m
        for p in parents:
            node = node.get(p) if isinstance(node, dict) else None
        if isinstance(node, dict) and isinstance(node.get(leaf), str):
            node[leaf] = [node[leaf]]
            findings.append(("warning", "DEP003", f"{path}: código isolado aceite; declarar como lista"))
    return m

def load(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--rules", default=str(ROOT / "spec" / "rules_v1_3_1.yaml"))
    ap.add_argument("--schema", default=str(ROOT / "spec" / "manifest.schema.json"))
    a = ap.parse_args()
    out = validate(load(a.manifest), load(a.rules), json.loads(Path(a.schema).read_text()))
    for lvl, rid, msg in out:
        print(f"{lvl.upper():8} {rid:7} {msg}")
    errors = sum(1 for f in out if f[0] == "error")
    print(f"\n{errors} erro(s), {sum(1 for f in out if f[0]=='warning')} aviso(s)")
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
