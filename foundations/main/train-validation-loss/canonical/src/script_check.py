"""Check the narration against the real run, and estimate its length.

Usage (from the film folder):
    python -B src/script_check.py [--report qa/script-report.json]

Checks, per line:
  * every claim's `show` equals the value read from its source(s), formatted by `fmt`
  * every claim's `say` equals the Korean reading of `show` (src/ko_numbers.py)
  * the shows appear in `text` in order, the says appear in `tts` in order
  * `tts` has no digits or % left (TTS reads Hangul only)
  * named `checks` (curve shape facts) hold on the full loss log
Per scene: every number on screen is one of the scene's claims.
Exit code 1 on any failure.  Timing is an estimate (syllables / rate + pauses),
not a measurement; real timing comes from the recorded voice.
"""
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from ko_numbers import READERS  # noqa: E402

RATE_SYL_PER_SEC = 5.5   # calm lecture pace (assumption, replaced by measured VO)
PAUSE_SENTENCE = 0.45
PAUSE_COMMA = 0.2
SCENE_TAIL = 0.6


def dig(obj, path):
    for key in path.split("."):
        obj = obj[int(key)] if isinstance(obj, list) else obj[key]
    return obj


def source_value(src, ctx):
    if src.startswith("min:") or src.startswith("max:"):
        vals = source_value(src[4:], ctx)
        return (min if src.startswith("min:") else max)(vals.values())
    kind, _, path = src.partition(":")
    if kind == "summary":
        return dig(ctx["summary"], path)
    if kind == "config":
        return dig(ctx["config"], path)
    if kind == "count":
        return len([s for s in (ROOT / "fixtures" / path).read_text(encoding="utf-8").splitlines() if s])
    if kind == "math":
        return eval(path, {"__builtins__": {}}, {"log": math.log})
    raise ValueError(src)


def fmt(v, how):
    if how == "2f":
        return f"{v:.2f}"
    if how == "round0":
        return str(int(round(v)))
    if how == "floor0":
        return str(int(math.floor(v)))
    if how == "int":
        assert float(v) == int(v), v
        return str(int(v))
    if how == "comma":
        assert float(v) == int(v), v
        return f"{int(v):,}"
    if how == "pct0":
        return f"{int(round(v * 100))}%"
    if how == "pct2":
        return f"{v * 100:.2f}%"
    if how == "man_cheon":
        n = int(round(v / 1000.0))
        man, cheon = divmod(n, 10)
        return f"{man}만" + (f" {cheon}천" if cheon else "")
    if how == "str":
        return str(v)
    if how == "drop_last":
        return str(v)[:-1]
    raise ValueError(how)


def check_claim(c, ctx):
    errs = []
    if c.get("src", "literal") != "literal":
        srcs = c["src"] if isinstance(c["src"], list) else [c["src"]]
        for s in srcs:
            got = fmt(source_value(s, ctx), c["fmt"])
            if got != c["show"]:
                errs.append(f"{c['show']!r} != {got!r} from {s}")
    if "say" in c:
        want = READERS[c["read"]](c["show"])
        if want != c["say"]:
            errs.append(f"reading of {c['show']!r} is {want!r}, script says {c['say']!r}")
    return errs


def in_order(hay, needles):
    pos = 0
    for n in needles:
        i = hay.find(n, pos)
        if i < 0:
            return n
        pos = i + len(n)
    return None


def curve_checks(name, ctx):
    run = ctx["runs"]["small"]
    log, best, final = run["log"], run["best"], run["final"]
    after = [row for row in log if row["step"] >= best["step"]]
    if name == "train_falls_after_best":
        rises = [b["train"] - a["train"] for a, b in zip(after, after[1:])]
        return final["train"] < best["train"] and max(rises) <= 1e-4
    if name == "val_rises_after_best":
        return final["val"] > best["val"] and all(row["val"] >= best["val"] for row in after)
    if name == "train_below_train_floor":
        return final["train"] < run["floor_train"]
    raise ValueError(name)


def syllables(text):
    return sum(1 for ch in text if "가" <= ch <= "힣")


def estimate(tts):
    sentences = len(re.findall(r"[.?!]", tts)) or 1
    return syllables(tts) / RATE_SYL_PER_SEC + sentences * PAUSE_SENTENCE + tts.count(",") * PAUSE_COMMA


def check(script, ctx):
    errors, scenes = [], []
    total = 0.0
    for sc in script["scenes"]:
        shows = []
        sec = 0.0
        for line in sc["lines"]:
            where = line["id"]
            for c in line["claims"]:
                errors += [f"{where}: {e}" for e in check_claim(c, ctx)]
            miss = in_order(line["text"], [c["show"] for c in line["claims"]])
            if miss:
                errors.append(f"{where}: show {miss!r} not in text (in order)")
            miss = in_order(line["tts"], [c["say"] for c in line["claims"]])
            if miss:
                errors.append(f"{where}: say {miss!r} not in tts (in order)")
            if re.search(r"[0-9%]", line["tts"]):
                errors.append(f"{where}: digits or % left in tts")
            for name in line.get("checks", []):
                if not curve_checks(name, ctx):
                    errors.append(f"{where}: curve check failed: {name}")
            shows += [c["show"] for c in line["claims"]]
            sec += estimate(line["tts"])
        for c in sc.get("screen_claims", []):
            errors += [f"{sc['id']} screen: {e}" for e in check_claim(c, ctx)]
            shows.append(c["show"])
        for txt in sc["screen"]:
            rest = txt
            for s in sorted(set(shows), key=len, reverse=True):
                rest = rest.replace(s, "")
            if re.search(r"\d", rest):
                errors.append(f"{sc['id']} screen: unverified number in {txt!r}")
        sec += SCENE_TAIL
        total += sec
        scenes.append({"id": sc["id"], "recipe": sc["recipe"], "lines": len(sc["lines"]),
                       "syllables": sum(syllables(l["tts"]) for l in sc["lines"]),
                       "est_sec": round(sec, 1)})
    return errors, {"scenes": scenes, "est_total_sec": round(total, 1),
                    "syllables": sum(s["syllables"] for s in scenes),
                    "assumption": f"{RATE_SYL_PER_SEC} 음절/초 + 문장 끝 {PAUSE_SENTENCE}s + 쉼표 {PAUSE_COMMA}s + 장면 꼬리 {SCENE_TAIL}s. 추정치이며 녹음 실측으로 대체한다."}


def load_ctx():
    summary = json.loads((ROOT / "results/summary.json").read_text(encoding="utf-8"))
    config = json.loads((ROOT / "fixtures/config.json").read_text(encoding="utf-8"))
    runs = {k: json.loads((ROOT / f"results/run-{k}.json").read_text(encoding="utf-8")) for k in summary["runs"]}
    return {"summary": summary, "config": config, "runs": runs}


def main(argv):
    script = json.loads((ROOT / "script/narration.json").read_text(encoding="utf-8"))
    errors, report = check(script, load_ctx())
    report["errors"] = errors
    report["claims"] = sum(len(l["claims"]) for sc in script["scenes"] for l in sc["lines"])
    report["status"] = "PASS" if not errors else "FAIL"
    if "--report" in argv:
        out = ROOT / argv[argv.index("--report") + 1]
        out.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("status", "claims", "syllables", "est_total_sec")}, ensure_ascii=False))
    for e in errors:
        print("FAIL", e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
