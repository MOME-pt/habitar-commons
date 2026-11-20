#!/usr/bin/env python3
"""Habitar Commons — validador de referência (v2.0-rc1).

Uso:  python validator/validate.py <manifesto.yaml> [--rules spec/rules_v2_0.yaml]

Verifica, por esta ordem:
  1. sinónimos obsoletos (aceites com aviso até à v3.0);
  2. o esquema (spec/manifest.schema.json): campos, tipos e códigos;
  3. as regras do ruleset, incluindo a derivação do headline (HL001).

Licença: CC BY-SA 4.0. Francisco Rocha Antunes, Filipa Serôdio Pinheiro · MOME, Porto.
O validador verifica a coerência interna do manifesto (níveis sintático e semântico).
Não verifica a conformidade jurídica nem o funcionamento real: esses níveis exigem
verificação humana e avaliação pós-ocupação.
"""
import copy, json, re, sys, argparse
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
MISSING = object()
PLACEHOLDER_KEYS = {"type", "description", "unit", "required_if"}

# ── caminhos ────────────────────────────────────────────────────────────────
TOKEN = re.compile(r"([^.\[\]]+)(\[(\*|[a-z_]+=[^\]]+)\])?")

def resolve(doc, path):
    """Valor no caminho, ou MISSING. Suporta a.b, lista[*].campo e lista[id=X].campo."""
    cur, multi = [doc], False
    for name, _, sel in TOKEN.findall(path):
        nxt = []
        for node in cur:
            if isinstance(node, dict) and name in node:
                nxt.append(node[name])
        if not nxt:
            return [] if multi else MISSING
        if sel:
            out = []
            for node in nxt:
                if not isinstance(node, list):
                    continue
                if sel == "*":
                    out.extend(node)
                else:
                    k, v = sel.split("=", 1)
                    out.extend(i for i in node if isinstance(i, dict) and str(i.get(k)) == v)
            if sel == "*":
                multi = True
            elif not out:
                return MISSING
            nxt = out
        cur = nxt
    if multi:
        flat = []
        for x in cur:
            flat.extend(x if isinstance(x, list) else [x])
        return flat
    return cur[0] if cur else MISSING

def has_value(v):
    if v is MISSING or v is None:
        return False
    if isinstance(v, str):
        return v.strip() != ""
    if isinstance(v, (list, tuple)):
        return len(v) > 0
    if isinstance(v, dict):
        if not v or set(v.keys()) <= PLACEHOLDER_KEYS:   # objeto de esquema, não um valor
            return False
        if "value" in v:
            return has_value(v["value"])
        return any(has_value(x) for x in v.values())
    return True

def codes(v):
    """Códigos de um eixo: lista, objeto com papéis ({base: E-COST, cap: E-CAP}) ou escalar."""
    if isinstance(v, dict):
        return [x for x in v.values() if isinstance(x, str)]
    return v if isinstance(v, list) else [v]

# ── derivações publicadas (decisões 37, 38, 54 e 64) ─────────────────────────
BASE_BY_RIGHT = [("R-OWN", "OWN"), ("R-LEASE", "LEASE"), ("R-LIC", "LIC"), ("R-TEMP", "TEMP"),
                 ("R-REAL-LIM", "REAL"), ("R-MEMB", "MEMB")]

def derive_headline(m):
    """H-<BASE>-<ECON>-<TERM>-<LOCK>, a partir dos eixos de PH-OP."""
    ax = m.get("axes", {})
    right = ax.get("resident_right") or ""
    econ = ax.get("economics") or {}
    if isinstance(econ, str):
        econ = {"base": econ}
    ecodes = codes(econ)
    owner = ax.get("asset_owner") or {}
    rel = (m.get("overlays") or {}).get("relational") or []
    if "MEMB" in (ax.get("right_condition") or []) or right == "R-MEMB":
        base = "MEMB"
    elif "E-HYB" in ecodes:
        base = "HYB"
    elif owner.get("nature") in ("A-FUND", "A-ASSOC") and owner.get("regime") == "AR-BOUND" and right != "R-OWN":
        base = "GUARD"
    elif "O-COHOUS" in rel and right == "R-OWN":
        base = "COHO"
    else:
        base = next((b for r, b in BASE_BY_RIGHT if right.startswith(r)), "?")
    if "E-RELEASE" in ecodes:
        e = "E-RELEASE"
    elif "E-ENTRY" in ecodes:
        e = "E-ENTRY"
    elif econ.get("income") == "E-INCOME" or econ.get("base") == "E-INCOME":
        e = "E-INCOME"
    elif econ.get("base") == "E-HYB":
        e = econ.get("cap", "E-HYB")
    else:
        e = econ.get("base", "E-?")
    term = ((ax.get("term") or {}).get("category") or "T-?")[2:]
    lock = ((ax.get("lock") or {}).get("code") or "L-?")[2:]
    return f"H-{base}-{e[2:]}-{term}-{lock}"

CORE_FUNCTIONS = ["sleep", "hygiene", "cook", "living"]

def derive_spatial(m):
    """Descritores espaciais derivados da matriz funcional e do inventário (M1)."""
    f = m.get("functions") or {}
    unit = m.get("unit") or {}
    out = ["O-UNIT" if all((f.get(k) or {}).get("where") == "unit" for k in CORE_FUNCTIONS) else "O-UNIT-PART"]
    if (unit.get("households") or 1) > 1:
        out.append("O-SHARE")
    limit = (m.get("parameters") or {}).get("micro_threshold_m2")
    if limit and unit.get("area_m2") and unit["area_m2"] < limit and \
            any((v or {}).get("where") == "common_required" for v in f.values()):
        out.append("O-MICRO")
    if any(s.get("function") != "circulacao" for s in (m.get("common_spaces") or [])):
        out.append("O-COMMON")
    return out

LOCK_RANK = {"L-0": 0, "L-INIT": 1, "L-TERM": 2, "L-SURF": 3, "L-PERP": 4}
VC_RANK = {"V-FREE": 0, "V-SHARED": 1, "V-CAP": 2, "V-0": 3}

def history_reductions(m):
    h = [x for x in (m.get("history") or []) if isinstance(x, dict)]
    out = []
    for a, b in zip(h, h[1:]):
        if LOCK_RANK.get(b.get("lock"), 9) < LOCK_RANK.get(a.get("lock"), -1):
            out.append(f"vinculação {a.get('lock')} → {b.get('lock')} ({b.get('version')})")
        if VC_RANK.get(b.get("value_capture"), 9) < VC_RANK.get(a.get("value_capture"), -1):
            out.append(f"captura de valor {a.get('value_capture')} → {b.get('value_capture')} ({b.get('version')})")
        lost = set(a.get("safeguards") or []) - set(b.get("safeguards") or [])
        if lost:
            out.append(f"salvaguardas retiradas: {', '.join(sorted(lost))} ({b.get('version')})")
    return out

def placeholders(v, path=""):
    if isinstance(v, dict):
        if v and set(v) <= PLACEHOLDER_KEYS:
            return [path]
        if "value" in v and not has_value(v["value"]):
            return [path]
        out = []
        for k, x in v.items():
            out += placeholders(x, f"{path}.{k}" if path else k)
        return out
    return [path] if v is None else []

# ── condições ───────────────────────────────────────────────────────────────
class Ctx:
    def __init__(self, manifest, ruleset):
        self.doc = dict(manifest)
        self.doc.setdefault("catalog", ruleset.get("catalog", {}))
        self.template = manifest.get("kind") == "template"
        self.pending = []
        self.detail = []

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
    op = cond["op"]
    if op == "always":
        return True
    if op == "headline_derived":
        d = derive_headline(ctx.doc)
        if ctx.doc.get("headline") != d:
            ctx.detail.append(f"declarado {ctx.doc.get('headline')}, derivado {d}")
            return False
        return True
    if op == "spatial_derived":
        d = derive_spatial(ctx.doc)
        decl = (ctx.doc.get("overlays") or {}).get("spatial") or []
        if sorted(decl) != sorted(d):
            ctx.detail.append(f"declarado {decl}, derivado {d}")
            return False
        return True
    if op == "history_monotonic":
        r = history_reductions(ctx.doc)
        ctx.detail += r
        return not r
    path = cond["path"]
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
    if op == "no_placeholders":
        p = placeholders(v, path) if v is not MISSING else []
        ctx.detail += p
        return not p
    if op == "each_sum_eq":            # para cada elemento da lista, soma do subcampo
        if v is MISSING:
            return False
        bad = [i.get("id", n) for n, i in enumerate(v)
               if abs(sum(as_list(resolve(i, cond["field"])) or [0]) - float(target)) > 1e-3]
        ctx.detail += [f"fluxo {b}" for b in bad]
        return not bad
    if v is MISSING or target is MISSING:
        return False
    if op in ("eq", "ne", "in", "not_in", "startswith"):
        if isinstance(v, list):
            raise TypeError(f"operador de escalar '{op}' aplicado à lista em {path}")
        return {"eq": lambda: v == target, "ne": lambda: v != target,
                "in": lambda: v in as_list(target), "not_in": lambda: v not in as_list(target),
                "startswith": lambda: isinstance(v, str) and v.startswith(target)}[op]()
    if op in ("contains", "contains_any", "contains_all", "contains_none", "subset_of", "contains_other_than"):
        if isinstance(v, dict):
            v = codes(v)
        if not isinstance(v, list):
            raise TypeError(f"operador de lista '{op}' aplicado ao escalar em {path}")
        t = as_list(target)
        return {"contains": lambda: target in v,
                "contains_any": lambda: any(x in v for x in t),
                "contains_all": lambda: all(x in v for x in t),
                "contains_none": lambda: not any(x in v for x in t),
                "subset_of": lambda: all(x in t for x in v),
                "contains_other_than": lambda: any(x not in t for x in v)}[op]()
    raise ValueError(f"operador desconhecido: {op}")

# ── sinónimos obsoletos (aceites com aviso até à v3.0) ──────────────────────
LIST_FIELDS = ["axes.finance", "axes.governance", "axes.safeguards", "axes.revision", "axes.population",
               "axes.right_condition", "modules.use", "modules.mobility", "modules.improvements",
               "modules.intermediation", "operation.public.developer", "operation.public.allocator"]
OSERV = {"O-SERV-0": [], "O-SERV-BASIC": ["SV-RES"], "O-SERV-ALLIN": ["SV-RES", "SV-DOM"]}
SPATIAL = ("O-UNIT", "O-UNIT-PART", "O-SHARE", "O-MICRO", "O-COMMON")

def normalize(m, findings):
    m = copy.deepcopy(m)
    ax = m.setdefault("axes", {})
    if m.get("kind") == "license":
        findings.append(("warning", "DEP001", "kind: license está obsoleto; usar kind: template"))
        m["kind"] = "template"
    if "license" in m and "spec_license" not in m:
        findings.append(("warning", "DEP002", "o campo license está obsoleto; usar spec_license"))
        m["spec_license"] = m.pop("license")
    for k in ("asset_owner", "land_owner"):
        if isinstance(ax.get(k), str):
            code = ax[k]
            msg = ("A-TRUST está obsoleto; declarar natureza (A-FUND ou A-ASSOC), regime (AR-*) e finalidade (PU-*)"
                   if code == "A-TRUST" else "código isolado aceite; declarar {nature, regime, purpose}")
            findings.append(("warning", "DEP004", f"axes.{k}: {msg}"))
            ax[k] = {"nature": code}
    sg = ax.get("safeguards")
    if isinstance(sg, list) and any(x in ("S-VULN", "S-ESC") for x in sg):
        findings.append(("warning", "DEP005", "S-VULN passa a S-PROT-VULN; S-ESC passa a parameters.sanctions_procedure"))
        ax["safeguards"] = ["S-PROT-VULN" if x == "S-VULN" else x for x in sg if x != "S-ESC"]
    ov = m.get("overlays")
    if isinstance(ov, list):
        findings.append(("warning", "DEP006", "overlays numa lista única: declarar por família (spatial, relational, programmatic)"))
        sv = [s for o in ov if o in OSERV for s in OSERV[o]]
        m["overlays"] = {"spatial": [o for o in ov if o in SPATIAL],
                         "relational": [o for o in ov if o in ("O-COLIV", "O-COHOUS")],
                         "programmatic": [o for o in ov if o in ("O-LIVEWORK", "O-PROD", "O-EQUIP")]}
        if any(o in OSERV for o in ov):
            findings.append(("warning", "DEP006", "O-SERV-* descontinuados: declarar serviços SV-*"))
            m.setdefault("services", [{"code": s} for s in sv])
    # forma v1.x dos eixos: convertida com aviso, para que o manifesto possa ser lido
    ROLE_OF = {"E-CAP": "cap", "E-SUB": "sub", "E-INCOME": "income", "E-ENTRY": "entry"}
    conv = []
    if isinstance(ax.get("economics"), (list, str)):
        lst = as_list(ax["economics"])
        e = {"base": lst[0]} if lst else {}
        for x in lst[1:]:
            e.setdefault(ROLE_OF.get(x, "services"), x)
        ax["economics"] = e; conv.append("economics")
    for k, key in (("term", "category"), ("lock", "code"), ("transfer", "code"), ("value_capture", "resident")):
        if isinstance(ax.get(k), str):
            ax[k] = {key: ax[k]}; conv.append(k)
    if isinstance(m.get("operation"), dict) and "public" not in m["operation"]:
        m["operation"] = {"public": m["operation"]}; conv.append("operation")
    if conv:
        findings.append(("warning", "DEP009", f"forma v1.x convertida: {', '.join(conv)}; rever o manifesto segundo a v2.0"))
    if "payer" in ax:
        findings.append(("warning", "DEP007", "axes.payer está obsoleto: declarar payer em cada fluxo (flows)"))
        ax.pop("payer")
    for path in LIST_FIELDS:
        *parents, leaf = path.split(".")
        node = m
        for p in parents:
            node = node.get(p) if isinstance(node, dict) else None
        if isinstance(node, dict) and isinstance(node.get(leaf), str):
            node[leaf] = [node[leaf]]
            findings.append(("warning", "DEP003", f"{path}: código isolado aceite; declarar como lista"))
    hl = m.get("headline", "")
    if isinstance(hl, str) and hl.count("-") == 3:
        findings.append(("warning", "DEP008", "headline de três posições (v1.x): acrescentar a vinculação, H-<BASE>-<ECON>-<TERM>-<LOCK>"))
    return m

# ── validação ───────────────────────────────────────────────────────────────
def validate(manifest, ruleset, schema=None):
    findings = []
    m = normalize(manifest, findings)
    if schema is not None:
        try:
            import jsonschema
            val = jsonschema.Draft202012Validator(schema)
            for e in sorted(val.iter_errors(m), key=lambda e: list(e.path)):
                loc = ".".join(str(p) for p in e.path) or "(raiz)"
                findings.append(("error", "SCH", f"{loc}: {e.message}"))
        except ImportError:
            findings.append(("info", "SCH", "jsonschema não instalado: esquema não verificado"))
    juris = set(m.get("jurisdiction", []))
    public = m.get("visibility") == "public"
    ctx = Ctx(m, ruleset)
    for r in ruleset["rules"]:
        if r.get("jurisdiction") and not juris & set(r["jurisdiction"]):
            continue
        if r.get("scope") == "private" and public:
            findings.append(("info", r["id"], "não verificada: depende de campos privados da Camada 6"))
            continue
        ctx.detail = []
        try:
            fires = test(ctx, r["when"]) and ("then" not in r or not test(ctx, r["then"]))
        except TypeError as e:
            findings.append(("error", r["id"], f"regra mal aplicada ao esquema: {e}"))
            continue
        if fires:
            extra = f" [{'; '.join(ctx.detail)}]" if ctx.detail else ""
            findings.append((r["severity"], r["id"], r["message"] + extra))
    for p in dict.fromkeys(ctx.pending):
        findings.append(("info", "TPL", f"a preencher por projeto: {p}"))
    return findings

def load(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--rules", default=str(ROOT / "spec" / "rules_v2_0.yaml"))
    ap.add_argument("--schema", default=str(ROOT / "spec" / "manifest.schema.json"))
    a = ap.parse_args()
    out = validate(load(a.manifest), load(a.rules), json.loads(Path(a.schema).read_text(encoding="utf-8")))
    for lvl, rid, msg in out:
        print(f"{lvl.upper():8} {rid:7} {msg}")
    errors = sum(1 for f in out if f[0] == "error")
    print(f"\n{errors} erro(s), {sum(1 for f in out if f[0] == 'warning')} aviso(s)")
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
