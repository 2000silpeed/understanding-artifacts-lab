"""Write results/table.md from results/summary.json (never edit the table by hand).

Usage (from the film folder):  python -B src/make_table.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    s = json.loads((ROOT / "results/summary.json").read_text(encoding="utf-8"))
    runs = s["runs"]
    rows = [
        ("훈련 문장 수", lambda r: r["n_train_sentences"]),
        ("매개변수 수", lambda r: f"{r['n_params']:,}"),
        ("0걸음 훈련 / 검증 손실", lambda r: f"{r['start']['train']:.4f} / {r['start']['val']:.4f}"),
        ("검증 손실 최저 걸음", lambda r: r["best"]["step"]),
        ("그때 훈련 / 검증 손실", lambda r: f"{r['best']['train']:.4f} / {r['best']['val']:.4f}"),
        ("3,000걸음 훈련 / 검증 손실", lambda r: f"{r['final']['train']:.4f} / {r['final']['val']:.4f}"),
        ("이론 바닥 (훈련 문장 / 검증 문장)", lambda r: f"{r['floor_train']:.4f} / {r['floor_val']:.4f}"),
        ("최저 시점 / 마지막 차이 (검증 − 훈련)", lambda r: f"{r['gap_best']:.4f} / {r['gap_final']:.4f}"),
        ("시험 손실 (최저 시점 모델 / 마지막 모델)", lambda r: f"{r['test']['best']:.4f} / {r['test']['final']:.4f}"),
        ("검증 퍼플렉서티 (최저 / 마지막 / 바닥)",
         lambda r: f"{r['ppl']['best_val']} / {r['ppl']['final_val']} / {r['ppl']['floor_val']}"),
        ("생성 200문장 중 훈련 문장 복사 (최저 / 마지막 / 진짜 분포 기대값)",
         lambda r: f"{r['generation']['best']['copies_of_train']} / {r['generation']['final']['copies_of_train']}"
                   f" / {r['generation']['final']['copies_expected_if_true']}"),
        ("생성 200문장 중 문법에 맞는 문장 (최저 / 마지막)",
         lambda r: f"{r['generation']['best']['grammatical']} / {r['generation']['final']['grammatical']}"),
        ("검증 문장 중 마지막에 더 나빠진 수 (128개 중)", lambda r: r["probe"]["val_sentences_worse"]),
    ]
    ids = list(runs)
    out = ["# 실험 결과표", "",
           "`src/make_table.py`가 `results/summary.json`에서 만든 표다. 손으로 고치지 않는다. 손실 단위는 글자당 nats.", "",
           "| 항목 | " + " | ".join(runs[i]["label"] for i in ids) + " |",
           "|---|" + "---|" * len(ids)]
    for name, f in rows:
        out.append(f"| {name} | " + " | ".join(str(f(runs[i])) for i in ids) + " |")
    who = s["probe_who"]
    out += ["", f"## '{who}' 다음 '언제' 칸 확률", "",
            "| 단어 | 진짜 | " + " | ".join(f"{runs[i]['label']}: 훈련 횟수 / 최저 시점 / 마지막" for i in ids) + " |",
            "|---|---|" + "---|" * len(ids)]
    for w in runs[ids[0]]["probe"]["train_counts"]:
        cells = []
        for i in ids:
            p = runs[i]["probe"]
            cells.append(f"{p['train_counts'][w]} / {p['best'][w]:.4f} / {p['final'][w]:.4f}")
        out.append(f"| {w} | {runs[ids[0]]['probe']['true_p']} | " + " | ".join(cells) + " |")
    out += ["", f"어휘 {s['vocab']}개, 무작위 추측 손실 ln({s['vocab']}) = {s['chance_loss']}. numpy {s['numpy']}.", ""]
    (ROOT / "results/table.md").write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    main()
