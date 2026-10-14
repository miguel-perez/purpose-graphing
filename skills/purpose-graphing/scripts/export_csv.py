"""Writes a study graph out as tables (Python 3.9+, standard library only).

Run from the study folder after the groups are recorded:

    python3 export_csv.py

It asks graph.py for the whole graph and writes three files under reports/.
Every line starts with the study's name, so tables from several studies can be
stacked into one repository or BI tool:

    groups.csv     one line per group: its level, label, parent group and how
                   many summaries and people sit under it
    summaries.csv  one line per summary for each lowest-level group it sits
                   in, with its level1, level2 and level3 groups side by side,
                   the account and the person's words; a summary in two
                   groups appears twice, and a summary in none appears once
                   with empty group columns
    rows.csv       one line per row, with its kind and any summary of it

Options: --out DIR (default reports; name the folder where the report was
saved when that isn't reports/), --graph PATH (default graph.py),
--study NAME (default: the name of the study folder).
"""
import argparse
import csv
import json
import os
import subprocess
import sqlite3
import sys
import tempfile

KINDS = {
    "1": "a particular moment",
    "2": "not tied to a moment",
    "3": "relationship to a topic",
    "4": "circumstances",
    "5": "none of these",
}
LEVELS = ("level1", "level2", "level3")


def has_graph(graph_path):
    db = os.path.join(os.path.dirname(os.path.abspath(graph_path)), "graph.db")
    if not os.path.isfile(db):
        return False
    try:
        con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
        try:
            return con.execute("select 1 from sqlite_master where type='table' and name='nodes'").fetchone() is not None
        finally:
            con.close()
    except sqlite3.Error:
        return False


def read_graph(graph_path):
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "graph.jsonl")
        r = subprocess.run([sys.executable, "-B", os.path.abspath(graph_path), "export", "--out", out],
                           cwd=os.path.dirname(os.path.abspath(graph_path)), capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit("export_csv: graph.py export failed: " + (r.stderr or r.stdout).strip())
        nodes, relations = {}, []
        with open(out, encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                if d.get("type") == "node":
                    nodes[d["id"]] = d
                elif d.get("type") == "relation":
                    relations.append(d)
    return nodes, relations


def order(ids):
    def key(i):
        digits = "".join(c for c in i if c.isdigit())
        return (int(digits) if digits else 0, i)
    return sorted(ids, key=key)


def tables(nodes, relations):
    parent, groups_of, summary_of, account_of, aside = {}, {}, {}, {}, set()
    for r in relations:
        k = r["kind"]
        if k == "part-of":
            parent[r["from"]] = r["to"]
        elif k == "member-of":
            groups_of.setdefault(r["from"], []).append(r["to"])
        elif k == "summarizes":
            summary_of[r["from"]] = r["to"]
        elif k == "drawn-from":
            account_of[r["from"]] = r["to"]
        elif k == "set-aside":
            aside.add(r["from"])
    groups = {i: n for i, n in nodes.items() if n["kind"] == "group"}

    def chain(gid):
        """The group and its ancestors, keyed by level."""
        out, seen = {}, set()
        while gid and gid in groups and gid not in seen:
            seen.add(gid)
            out[groups[gid].get("level", "")] = gid
            gid = parent.get(gid)
        return out

    def words(eid):
        return " | ".join(f.get("text", "") for f in nodes.get(eid, {}).get("fragments", []))

    summaries = order(i for i, n in nodes.items() if n["kind"] == "summary")
    below = {g: set() for g in groups}
    summary_rows = []
    for sid in summaries:
        eid = summary_of.get(sid, "")
        account = account_of.get(eid, "")
        homes = groups_of.get(sid, [])
        status = "set aside" if sid in aside else ("placed" if homes else "unplaced")
        for home in (order(homes) or [None]):
            c = chain(home) if home else {}
            for gid in c.values():
                below[gid].add((sid, account))
            line = []
            for lv in LEVELS:
                gid = c.get(lv, "")
                line += [gid, groups[gid].get("label", "") if gid else ""]
            summary_rows.append(line + [sid, nodes[sid].get("text", ""), status, account, eid, words(eid)])

    group_rows = []
    for lv in reversed(LEVELS):
        for gid in order(g for g in groups if groups[g].get("level") == lv):
            p = parent.get(gid, "")
            members = below[gid]
            group_rows.append([gid, lv, groups[gid].get("label", ""), p, groups[p].get("label", "") if p else "",
                               len({s for s, _ in members}), len({a for _, a in members if a})])

    summary_text = {s: nodes[s].get("text", "") for s in summaries}
    by_row = {e: s for s, e in summary_of.items()}
    row_rows = []
    for eid in order(i for i, n in nodes.items() if n["kind"] == "evidence"):
        kind = str(nodes[eid].get("evidenceKind", ""))
        sid = by_row.get(eid, "")
        row_rows.append([eid, account_of.get(eid, ""), kind, KINDS.get(kind, ""), words(eid), sid, summary_text.get(sid, "")])
    return group_rows, summary_rows, row_rows


HEADERS = {
    "groups.csv": ["study", "group_id", "level", "label", "parent_id", "parent_label", "summaries", "people"],
    "summaries.csv": ["study", "level1_id", "level1_label", "level2_id", "level2_label", "level3_id", "level3_label",
                      "summary_id", "summary", "status", "account", "row_id", "words"],
    "rows.csv": ["study", "row_id", "account", "kind", "kind_name", "words", "summary_id", "summary"],
}


def main(argv=None):
    p = argparse.ArgumentParser(prog="export_csv.py", description="Write the study graph out as CSV tables.")
    p.add_argument("--out", default="reports", help="folder for groups.csv, summaries.csv and rows.csv")
    p.add_argument("--graph", default="graph.py", help="path to the study's graph.py")
    p.add_argument("--study", default=None, help="name for this study in every line (default: the study folder's name)")
    a = p.parse_args(argv)
    if not os.path.isfile(a.graph):
        raise SystemExit("export_csv: no graph.py at %s; run this from the study folder or pass --graph" % a.graph)
    if not has_graph(a.graph):
        raise SystemExit("export_csv: no study graph next to %s; set the study up first" % a.graph)
    group_rows, summary_rows, row_rows = tables(*read_graph(a.graph))
    study = a.study or os.path.basename(os.path.dirname(os.path.abspath(a.graph)))
    os.makedirs(a.out, exist_ok=True)
    for name, rows in (("groups.csv", group_rows), ("summaries.csv", summary_rows), ("rows.csv", row_rows)):
        path = os.path.join(a.out, name)
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(HEADERS[name])
            w.writerows([study] + r for r in rows)
        print(path)


if __name__ == "__main__":
    main()
