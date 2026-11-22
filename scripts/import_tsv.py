FRAMING_PRIMARY = ("cowboy shot", "upper body", "close-up", "pov")
FRAMING_SECOND = ("from below", "from above", "over the shoulder", "mirror reflection")
SLUGS_FILE = ROOT / "config" / "slugs.txt"


def load_slugs() -> set:
    if not SLUGS_FILE.exists():
        return set()
    return {l.strip() for l in SLUGS_FILE.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.startswith("#")}


def snap_slug(p: str, slugs: set) -> tuple:
    if not slugs or p in slugs:
        return p, []
    toks = set(p.split("_"))
    best, score = None, 0
    for s in slugs:
        sc = len(toks & set(s.split("_")))
        if sc > score:
            best, score = s, sc
    if best and score >= 2:
        return best, [f"place辞書補正 {p}->{best}"]
    return p, [f"place辞書外 {p}"]


def normalize_fields(ins: str, mot: str) -> tuple:
    """instruction/motion の汚染を剥がす。"""
    fixes = []
    if "camera locked" in ins:
        ins = ins.replace("camera locked", "")
        fixes.append("instructionからcamera locked除去")
    ins = re.sub(r"\bupper body focus\b", "upper body", ins)
    ins = re.sub(r"\bfull body\b", "cowboy shot", ins)
    ins = re.sub(r"\bfrom front\b", "", ins)

    tags = [t.strip() for t in ins.split(",") if t.strip()]
    prim = [t for t in tags if t in FRAMING_PRIMARY]
    if prim:
        head = prim[0]
        tags = [t for t in tags if t not in FRAMING_PRIMARY]
        tags.insert(0, head)
    sec = [t for t in tags if t in FRAMING_SECOND][:1]
    tags = [t for t in tags if t not in FRAMING_SECOND] + sec

    has_ins = any("inserted" in t for t in tags)
    has_cum = any(("creampie" in t or "cum overflow" in t) for t in tags)
    if has_ins and has_cum:
        tags = [t for t in tags if "inserted" not in t]
        fixes.append("penis inserted除去(creampieと競合)")

    tags = list(dict.fromkeys(tags))
    ins = ", ".join(tags).strip(" ,")

    mtags = [t.strip() for t in mot.split(",") if t.strip()]
    before = len(mtags)
    mtags = [t for t in mtags if t not in tags and t != "camera locked"]
    if len(mtags) != before:
        fixes.append("motion重複除去")
    mtags.append("camera locked")
    mot = ", ".join(dict.fromkeys(mtags))
    return ins, mot, fixes
