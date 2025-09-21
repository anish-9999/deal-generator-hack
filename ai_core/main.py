from __future__ import annotations
import argparse, json
from .deal_note_generator import generate_deal_note

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", action="append", required=True, help="Path to PDF/PPT(X). Repeatable.")
    ap.add_argument("--type", action="append", required=False, help="Type for each file (pdf|ppt|pptx).")
    ap.add_argument("--name", required=True, help="Startup name")
    ap.add_argument("--sector", default="SaaS")
    ap.add_argument("--stage", default="Seed")
    args = ap.parse_args()

    files = []
    for i, p in enumerate(args.file):
        ftype = (args.type[i] if args.type and i < len(args.type) else None)
        files.append({"path": p, "type": ftype})

    startup_meta = {"name": args.name, "sector": args.sector, "stage": args.stage}
    note = generate_deal_note(files, startup_meta)
    print(json.dumps(note, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

## inside your route handler e.g. POST /api/generate-note
# from ai_core.deal_note_generator import generate_deal_note

# payload = request.json  # {"files":[{"path":"/tmp/x.pdf","type":"pdf"}], "startup":{"name":"Acme AI","sector":"SaaS","stage":"Seed"}, "weights":{...}}
# note = generate_deal_note(payload["files"], payload["startup"], payload.get("weights"))
# return jsonify(note)
