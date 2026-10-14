#!/usr/bin/env python3
"""The study graph (Python 3.9+, standard library only).

Copy this file into a study folder and run it from there:

    python3 graph.py init --sources-dir FOLDER --question 'QUESTION'
    python3 graph.py help

init registers every .txt and .md file in FOLDER as an account, its id taken
from the file name, and the question. The graph is kept in graph.db beside this
file. The command names, help text and refusal wording are built in
(DEFAULT_SURFACE); --surface FILE replaces them and --db FILE moves the graph.

Exit codes: 0 success, 2 refusal (one line on stdout: refused <key>: <text>),
1 an error, its message on stderr.

Offsets are stored and exported in UTF-16 code units.
"""
import argparse
import difflib
import hashlib
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone

OPERATIONS = ["help", "add-evidence", "add-summary", "add-group", "link", "unlink",
              "relabel", "set-aside", "show", "list", "find"]
REFUSALS = ["fragment-not-found", "fragment-ambiguous", "fragment-outside-person", "unknown-id",
            "wrong-kind", "relation-not-allowed", "level-skip", "cycle", "duplicate",
            "empty-text", "text-too-long", "bad-argument"]
FLAG_KEYS = ["source", "kind", "text", "occurrence", "of", "level", "label", "in", "page", "detail"]
RESERVED_VERBS = ["init", "export"]
NOT_SET_UP = ("the graph is not set up yet; from the study folder run: "
              "python3 graph.py init --sources-dir FOLDER --question 'QUESTION'")
DEFAULT_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graph.db")

NODE_KINDS = ["source", "question", "evidence", "summary", "group"]
LEVELS = ["level1", "level2", "level3"]
PREFIX = {"evidence": "e", "summary": "s", "group": "g", "question": "q"}
# Relations the agent may make or remove with link and unlink. drawn-from and
# summarizes are made with the evidence and the summary and never change.
LINKABLE = ["member-of", "part-of", "addresses", "set-aside"]
ALLOWED = ("member-of: summary to level1 group; part-of: level1 group to level2 group, level2 group to level3 group; "
           "addresses: group to question; set-aside: summary or evidence to question")
MAX_CHARS = {"fragment": 2000, "summary": 600, "label": 200, "find": 200}
GENERATED_ID = re.compile(r"^[esgq][0-9]+$")
SOURCE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class Refused(Exception):
    def __init__(self, key, **values):
        Exception.__init__(self, key)
        self.key = key
        self.values = values


class Failure(Exception):
    """An error in the graph or in its setup: exit 1."""


class Placeholders(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def one_line(text):
    """The account files wrap long turns by turning a space into a newline; a newline is read as a space."""
    return text.replace("\n", " ")


def utf16(text, i):
    return len(text[:i].encode("utf-16-le")) // 2


def code_point_index(text):
    """Map from each UTF-16 offset that falls on a character boundary to its code point index."""
    index, u = {0: 0}, 0
    for i, ch in enumerate(text):
        u += 2 if ord(ch) > 0xFFFF else 1
        index[u] = i + 1
    return index


def check_person_spans(source_id, text, spans):
    index = code_point_index(text)
    if not isinstance(spans, list) or not spans:
        raise Failure("source %s: personSpans must be a non-empty list of [start, end]" % source_id)
    end = -1
    for span in spans:
        if (not isinstance(span, list) or len(span) != 2 or not all(type(x) is int for x in span)):
            raise Failure("source %s: each person span must be [start, end] in whole numbers" % source_id)
        s, e = span
        if not (s < e) or s not in index or e not in index:
            raise Failure("source %s: person span [%d, %d] is empty, out of range or splits a character "
                          "(offsets are UTF-16 code units of the text)" % (source_id, s, e))
        if s < end:
            raise Failure("source %s: person spans must be in order and not overlap, at [%d, %d]" % (source_id, s, e))
        end = e


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def account_id(file_name):
    """An account id from a file name: the name without its extension, with every run of other
    characters than letters, digits, '.', '_' and '-' turned into one '-'."""
    stem = os.path.splitext(file_name)[0]
    s = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-._")[:128]
    if not s or GENERATED_ID.match(s):
        s = ("account-" + s).strip("-")[:128]
    return s


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# ---------------------------------------------------------------- surface

# The surface: the command names, help text and refusal wording the agent sees.
DEFAULT_SURFACE = json.loads(r"""
{
  "version": 1,
  "command": "graph.py",
  "verbs": {
    "help": "help",
    "add-evidence": "add-evidence",
    "add-summary": "add-summary",
    "add-group": "add-group",
    "link": "link",
    "unlink": "unlink",
    "relabel": "relabel",
    "set-aside": "set-aside",
    "show": "show",
    "list": "list",
    "find": "find"
  },
  "flags": {
    "source": "--source",
    "kind": "--kind",
    "text": "--text",
    "occurrence": "--occurrence",
    "of": "--of",
    "level": "--level",
    "label": "--label",
    "in": "--in",
    "page": "--page",
    "detail": "--detail"
  },
  "pageSize": 100,
  "detail": "concise",
  "help": "STUDY GRAPH\nRun from the study folder: python3 graph.py OPERATION ARGUMENTS. Run the graph; never read its program or configuration. Load the skill through the skill tool and read the instructions for your tasks. Each helper must load the skill independently.\n\nSTART\npython3 graph.py list question\npython3 graph.py list source\npython3 graph.py show ID --detail detailed\nAccounts and the question already exist. Reuse returned ids, not guessed ids or filenames. Read each conversation before selecting rows. Cover every account, retaining differences and contrary experiences. Record work progressively.\n\nROWS\npython3 graph.py add-evidence --source SOURCE_ID --kind K --text 'EXACT FRAGMENT' --text 'ANOTHER EXACT FRAGMENT'\nRepeat --text for separate fragments of one row. Each fragment must occur verbatim within a Person turn in that account. Never use Listener words, rewrite grammar, insert ellipses, or combine separated passages into one fragment. Keep enough wording to establish meaning and circumstances. Each row expresses one thing. Gather returns to that same thing into one row; separate distinct thoughts even if their purpose is similar.\nK selects the category:\n1: Thinking, noticing, weighing, deciding, or feeling at a particular past moment; also a personal rule that steered a decision then.\n2: Apparent moment-specific thinking that instead spans occasions, is only implied, or concerns a future or unexperienced situation.\n3: The person's relationship to a topic: approval, disapproval, preferences, settled views, or habits.\n4: Circumstances, events, facts, or explanations of how or why something works or is done.\n5: What fits none of these categories.\nClassify what the words express, not an inferred mental cause of an action. Collect all categories, not only passages supporting a likely answer.\nFor repeated wording, place --occurrence N immediately after the relevant --text value. N counts matches in Person turns from 1. Check which match is intended. Each fragment can have its own selector.\n\nSUMMARIES\npython3 graph.py add-summary --of EVIDENCE_ID --text 'SUMMARY'\nSummarize each category-1 row using its stored fragments. Use first person and present tense, starting with a verb for thinking or feeling. Retain what the thought or feeling concerns and its essential reason or condition. Do not substitute events for thinking, invent motives, or import facts from elsewhere in the account. Use one summary per row. If a row has no supported thinking or feeling to summarize, set it aside rather than fabricate; explain the exception in the report.\n\nGROUPS\npython3 graph.py add-group --level level1 --label 'SHARED MEANING'\npython3 graph.py link SUMMARY_ID member-of GROUP_ID\npython3 graph.py add-group --level level2 --label 'BROADER SHARED MEANING'\npython3 graph.py link LOWER_GROUP_ID part-of UPPER_GROUP_ID\npython3 graph.py add-group --level level3 --label 'BROAD SHARED MEANING'\nOptional on add-group: --in PARENT_GROUP_ID. The parent must be exactly one level higher.\nA level1 group holds summaries; level2 holds level1 groups; level3 holds level2 groups. Never skip levels. Build only useful levels, up to level3.\nGroup by shared meaning or purpose of the thinking, not topic words or similar actions alone. Test every member against its label. Keep important differences in separate groups. Labels should explain the shared meaning to an unfamiliar reader. A specific singleton is better than a false merger. Review across accounts before finalizing groups. Several rows from one person do not represent several people.\npython3 graph.py link GROUP_ID addresses QUESTION_ID\nUse addresses for groups that help answer the question; it does not replace membership links.\n\nREVIEW AND REPAIR\npython3 graph.py show ID --detail concise\npython3 graph.py show ID --detail detailed\npython3 graph.py list evidence --source SOURCE_ID --kind 1\npython3 graph.py list summary --source SOURCE_ID\npython3 graph.py list summary --in GROUP_ID\npython3 graph.py list summary --in none\npython3 graph.py list group --level level1\npython3 graph.py list group --in PARENT_GROUP_ID\nList kinds: source, question, evidence, summary, group. Filters: --source for evidence or summary; --kind for evidence; --level for group; --in for summary or group. --in none finds entries neither placed nor set aside. Pagination begins at 1; use --page 2 and continue until all entries have been reviewed.\npython3 graph.py find 'WORDS' --page 1\npython3 graph.py relabel GROUP_ID --label 'REVISED LABEL'\npython3 graph.py relabel SUMMARY_ID --text 'REVISED SUMMARY'\npython3 graph.py unlink FROM_ID RELATION TO_ID\nUnlink removes a relation, not an entry. Relation words are member-of, part-of, addresses, and set-aside.\npython3 graph.py set-aside EVIDENCE_OR_SUMMARY_ID\nEquivalent: python3 graph.py link EVIDENCE_OR_SUMMARY_ID set-aside QUESTION_ID\nKeep unsupported or uncertain material visible without forcing placement. Review unplaced summaries before setting them aside; explain meaningful exclusions in the report.\n\nFINISH\nCheck coverage of every account, summaries for category-1 rows, placement of every summary, and coherent group membership. Follow pagination. Retain returned ids. Duplicate notices reuse existing entries or links and are not failures. Repair refused commands before relying on them.\nWrite the report under reports/. Answer the question with supported findings, concrete circumstances, differences, and limitations. Readers must understand it without graph access; ids alone cannot explain findings. The graph keeps supporting work; the report explains what the accounts establish.",
  "refusals": {
    "fragment-not-found": "Fragment not found in account {source}: {text}. Closest available wording: {closest}. Recheck the account and copy the intended Person wording exactly. Supply separated passages as separate --text values.",
    "fragment-ambiguous": "The fragment {text} has {count} matches in Person turns of account {source}. Add --occurrence N immediately after this fragment's --text value, selecting the intended match in account order.",
    "fragment-outside-person": "The fragment {text} in account {source} is outside the Person turns. Rows must use the person's own words. Find supporting Person wording instead; do not attribute the Listener's words to the person.",
    "unknown-id": "No entry has id {id}. Use list or find to locate the entry, and reuse its returned id.",
    "wrong-kind": "Entry {id} is {actual}; this operation requires {expected}. Inspect the entry and choose an id of the required kind.",
    "relation-not-allowed": "Cannot link {from_id} ({from_kind}) to {to_id} ({to_kind}) using {relation}. Allowed relations: {allowed}. Check both endpoint kinds and the link direction.",
    "level-skip": "Cannot link {from_id} at {from_level} to {to_id} at {to_level} using {relation}. The required next level is {next_level}. Use an appropriate parent at that level; do not skip a level.",
    "cycle": "Linking {from_id} to {to_id} using {relation} would create a cycle. Choose a parent outside this group's descendants and check the link direction.",
    "duplicate": "Already recorded as {id}; the existing entry or link was reused. Continue with that id. This notice is not a failure.",
    "empty-text": "No words were supplied for {flag}. Provide meaningful text supported by the account. Usage: {usage}",
    "text-too-long": "The value for {flag} has length {length}; the maximum is {max}. Shorten summaries or labels without losing their meaning. For copied evidence, use shorter exact fragments without rewriting the person's words.",
    "bad-argument": "Invalid argument: {detail}. Usage: {usage}. Check the operation, positional arguments, flag names, and allowed values; quote text as a single shell argument."
  }
}
""")


def load_surface(path):
    try:
        with open(path, encoding="utf-8") as f:
            surface = json.load(f)
    except (OSError, ValueError) as e:
        raise Failure("cannot read the surface %s: %s" % (path, e))
    return check_surface(surface)


def check_surface(surface):
    verbs, flags, refusals = surface.get("verbs"), surface.get("flags"), surface.get("refusals")
    if not isinstance(verbs, dict) or sorted(verbs) != sorted(OPERATIONS):
        raise Failure("the surface's verbs must name exactly the operations %s" % ", ".join(OPERATIONS))
    if len(set(verbs.values())) != len(verbs) or any(v in RESERVED_VERBS for v in verbs.values()):
        raise Failure("the surface's verb names must be distinct and must not be init or export")
    if not isinstance(flags, dict) or sorted(flags) != sorted(FLAG_KEYS) or len(set(flags.values())) != len(flags):
        raise Failure("the surface's flags must name exactly %s, each distinctly" % ", ".join(FLAG_KEYS))
    if not isinstance(refusals, dict) or sorted(refusals) != sorted(REFUSALS):
        raise Failure("the surface's refusals must word exactly %s" % ", ".join(REFUSALS))
    if not isinstance(surface.get("help"), str) or not isinstance(surface.get("command"), str):
        raise Failure("the surface needs a help text and a command")
    page = surface.get("pageSize", 40)
    if not isinstance(page, int) or page < 1:
        raise Failure("the surface's pageSize must be a whole number from 1")
    surface["pageSize"] = page
    surface["detail"] = surface.get("detail", "concise")
    return surface


class Graph:
    def __init__(self, db_path, surface):
        self.surface = surface
        self.call = None
        self.verbs = surface["verbs"]
        self.flags = surface["flags"]
        self.command = "python3 " + surface["command"]
        self.db = sqlite3.connect(db_path, timeout=10, isolation_level=None)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA foreign_keys=ON")

    # ------------------------------------------------------------ helpers

    def verb(self, op):
        return self.verbs[op]

    def flag(self, key):
        return self.flags[key]

    def usage(self, op):
        f, c, v = self.flag, self.command, self.verb(op)
        forms = {
            "help": "",
            "add-evidence": '%s <source id> %s <1-5> %s "<words copied exactly>" [%s <n>] [%s "<more words>" ...]'
                            % (f("source"), f("kind"), f("text"), f("occurrence"), f("text")),
            "add-summary": '%s <evidence id> %s "<what it means, in the person\'s voice>"' % (f("of"), f("text")),
            "add-group": '%s <level1|level2|level3> %s "<label>" [%s <group id one level up>]'
                         % (f("level"), f("label"), f("in")),
            "link": "<from id> <member-of|part-of|addresses|set-aside> <to id>",
            "unlink": "<from id> <member-of|part-of|addresses|set-aside> <to id>",
            "relabel": '<group id> %s "<label>"  or  <summary id> %s "<text>"' % (f("label"), f("text")),
            "set-aside": "<summary or evidence id>",
            "show": "<id> [%s concise|detailed]" % f("detail"),
            "list": "<source|question|evidence|summary|group> [%s <source id>] [%s <1-5>] [%s <level>] [%s <group id>|none] [%s <n>]"
                    % (f("source"), f("kind"), f("level"), f("in"), f("page")),
            "find": '"<words>" [%s <n>]' % f("page"),
        }
        return ("%s %s %s" % (c, v, forms[op])).rstrip()

    # The detail of an unknown verb: the verbs the surface offers, in its own words, and how a wrong entry is undone,
    # since no verb removes anything.
    def no_such_command(self, token):
        return ("there is no command \"%s\". The commands are %s. There is no command that deletes: %s retracts a summary "
                "or a row; %s changes a group's label or a summary's text; a wrong row is set aside and added again"
                % (token, ", ".join(self.verb(op) for op in OPERATIONS), self.verb("set-aside"), self.verb("relabel")))

    def refusal_text(self, key, values):
        return self.surface["refusals"][key].format_map(Placeholders(values))

    def tables_exist(self):
        r = self.db.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='nodes'").fetchone()
        return r[0] == 1

    def node(self, node_id, expected=None):
        r = self.db.execute("SELECT id, kind, text, level, label, evidence_kind, fragments, person_spans FROM nodes WHERE id = ?",
                            (node_id,)).fetchone()
        if r is None:
            raise Refused("unknown-id", id=node_id)
        row = {"id": r[0], "kind": r[1], "text": r[2], "level": r[3], "label": r[4], "evidenceKind": r[5],
               "fragments": json.loads(r[6]) if r[6] else None, "personSpans": json.loads(r[7]) if r[7] else None}
        if expected is not None and row["kind"] not in expected:
            raise Refused("wrong-kind", id=node_id, actual=self.kind_name(row), expected=" or ".join(expected))
        return row

    @staticmethod
    def kind_name(row):
        return "%s group" % row["level"] if row["kind"] == "group" else row["kind"]

    def new_id(self, kind):
        prefix = PREFIX[kind]
        n = self.db.execute("SELECT COALESCE(MAX(seq), 0) FROM nodes WHERE kind = ?", (kind,)).fetchone()[0]
        while True:
            n += 1
            candidate = "%s%d" % (prefix, n)
            if self.db.execute("SELECT 1 FROM nodes WHERE id = ?", (candidate,)).fetchone() is None:
                return candidate, n

    def insert_node(self, kind, **fields):
        node_id, seq = self.new_id(kind)
        self.db.execute(
            "INSERT INTO nodes (id, kind, seq, text, sha256, level, label, evidence_kind, fragments, source, dupkey) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (node_id, kind, seq, fields.get("text"), None, fields.get("level"), fields.get("label"),
             fields.get("evidence_kind"), fields.get("fragments"), fields.get("source"), fields.get("dupkey")))
        return node_id

    def relation_exists(self, kind, a, b):
        return self.db.execute("SELECT 1 FROM relations WHERE kind=? AND src=? AND dst=?", (kind, a, b)).fetchone() is not None

    def add_relation(self, kind, a, b):
        self.db.execute("INSERT INTO relations (kind, src, dst) VALUES (?,?,?)", (kind, a, b))

    def the_question(self):
        r = self.db.execute("SELECT id FROM nodes WHERE kind='question' ORDER BY seq LIMIT 1").fetchone()
        if r is None:
            raise Failure("the graph holds no question; run init first")
        return r[0]

    def text_arg(self, value, flag_key, limit_key):
        if value is None or not value.strip():
            raise Refused("empty-text", flag=self.flag(flag_key), usage="")
        if len(value) > MAX_CHARS[limit_key]:
            raise Refused("text-too-long", flag=self.flag(flag_key), length=len(value), max=MAX_CHARS[limit_key])
        return value

    def write(self, fn):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            out = fn()
            # The call's log line goes into the same transaction as what it wrote, before COMMIT, so the log's order is
            # the order the graph created its nodes in, whatever other processes write at the same time.
            if self.call is not None:
                self.log(self.call[0], self.call[1], "duplicate" if self.note == "duplicate" else "ok", None)
                self.call = None
            self.db.execute("COMMIT")
            return out
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    # ------------------------------------------------------------ argument parsing

    def parser(self, op):
        graph = self

        class Parser(argparse.ArgumentParser):
            def error(self, message):
                raise Refused("bad-argument", detail=message, usage=graph.usage(op))

        return Parser(prog=self.usage(op), add_help=False, allow_abbrev=False)

    def parse(self, op, parser, rest):
        # Join each value flag with its value, so a value that begins with - is read as a value.
        value_flags = set(self.flags.values())
        joined, i = [], 0
        while i < len(rest):
            if rest[i] in value_flags and i + 1 < len(rest):
                joined.append("%s=%s" % (rest[i], rest[i + 1]))
                i += 2
            else:
                joined.append(rest[i])
                i += 1
        return parser.parse_args(joined)

    def page_arg(self, value):
        if value is None:
            return 1
        if not re.match(r"^[0-9]+$", value) or int(value) < 1:
            raise Refused("bad-argument", detail="%s takes a whole number from 1" % self.flag("page"), usage="")
        return int(value)

    # ------------------------------------------------------------ fragments

    @staticmethod
    def person_spans(text, given=None):
        """Spans (code points) of the person's words. Spans given at init (UTF-16, checked
        there) alone decide when present; otherwise the text after 'Person:' on each line
        that begins with it, or the whole text when no line begins with 'Listener:'."""
        if given is not None:
            index = code_point_index(text)
            return [(index[s], index[e]) for s, e in given]
        lines = text.split("\n")
        if not any(line.startswith("Listener:") for line in lines):
            return [(0, len(text))]
        spans, pos = [], 0
        for line in lines:
            if line.startswith("Person:"):
                start = pos + len("Person:")
                while start < pos + len(line) and line[start - pos] == " ":
                    start += 1
                spans.append((start, pos + len(line)))
            pos += len(line) + 1
        return spans

    @staticmethod
    def closest(text, spans, fragment):
        best, best_len = "", 0
        for s, e in spans:
            turn = text[s:e]
            m = difflib.SequenceMatcher(None, turn, fragment, autojunk=False).find_longest_match(0, len(turn), 0, len(fragment))
            if m.size > best_len:
                start = max(0, m.a - m.b)
                end = min(len(turn), start + max(len(fragment), m.size))
                best, best_len = turn[start:end], m.size
        if len(best) > 80:
            best = best[:80]
        return best

    def locate(self, source, fragment, occurrence):
        text = source["text"]
        spans = self.person_spans(text, source["personSpans"])
        # The account files wrap long turns by turning a space into a newline, so a newline and
        # a space are the same character here, on both sides. Lengths are equal, so offsets hold.
        flat, wanted = text.replace("\n", " "), fragment.replace("\n", " ")
        everywhere, inside, i = [], [], flat.find(wanted)
        while i != -1:
            everywhere.append(i)
            if any(s <= i and i + len(wanted) <= e for s, e in spans):
                inside.append(i)
            i = flat.find(wanted, i + 1)
        if not everywhere:
            raise Refused("fragment-not-found", source=source["id"], text=fragment,
                          closest=self.closest(flat, spans, wanted))
        if not inside:
            raise Refused("fragment-outside-person", source=source["id"], text=fragment)
        if occurrence is None:
            if len(inside) > 1:
                raise Refused("fragment-ambiguous", source=source["id"], text=fragment, count=len(inside))
            occurrence = 1
        if occurrence > len(inside):
            raise Refused("bad-argument",
                          detail="%s %d was given, but these words appear %d time(s) in the person's turns of %s"
                                 % (self.flag("occurrence"), occurrence, len(inside), source["id"]),
                          usage=self.usage("add-evidence"))
        start = inside[occurrence - 1]
        return {"text": fragment, "start": utf16(text, start), "end": utf16(text, start + len(fragment))}

    # ------------------------------------------------------------ agent operations

    def op_help(self, rest):
        self.parse("help", self.parser("help"), rest)
        return self.surface["help"]

    def op_add_evidence(self, rest):
        p = self.parser("add-evidence")
        texts, occurrences = [], {}

        class Text(argparse.Action):
            def __call__(self, parser, ns, value, option_string=None):
                texts.append(value)

        class Occurrence(argparse.Action):
            def __call__(self, parser, ns, value, option_string=None):
                if not texts:
                    parser.error("%s goes right after the %s it applies to" % (option_string, self_flag("text")))
                if not re.match(r"^[0-9]+$", value) or int(value) < 1:
                    parser.error("%s takes a whole number from 1" % option_string)
                occurrences[len(texts) - 1] = int(value)

        self_flag = self.flag
        p.add_argument(self.flag("source"), dest="source", required=True)
        p.add_argument(self.flag("kind"), dest="kind", required=True)
        p.add_argument(self.flag("text"), dest="text", action=Text, required=True)
        p.add_argument(self.flag("occurrence"), dest="occurrence", action=Occurrence)
        a = self.parse("add-evidence", p, rest)
        if a.kind not in ("1", "2", "3", "4", "5"):
            raise Refused("bad-argument", detail="%s takes one of 1, 2, 3, 4 or 5, not \"%s\"" % (self.flag("kind"), a.kind),
                          usage=self.usage("add-evidence"))
        kind = int(a.kind)
        for t in texts:
            self.text_arg(t, "text", "fragment")

        def run():
            source = self.node(a.source, ["source"])
            fragments = [self.locate(source, t, occurrences.get(i)) for i, t in enumerate(texts)]
            dupkey = json.dumps([source["id"], kind, sorted([f["start"], f["end"]] for f in fragments)])
            existing = self.db.execute("SELECT id FROM nodes WHERE kind='evidence' AND dupkey=?", (dupkey,)).fetchone()
            if existing:
                return self.duplicate(existing[0])
            node_id = self.insert_node("evidence", evidence_kind=kind, source=source["id"],
                                       fragments=json.dumps(fragments, ensure_ascii=False), dupkey=dupkey)
            self.add_relation("drawn-from", node_id, source["id"])
            return "%s\nevidence %s drawn-from %s, kind %d, %d fragment(s)" % (node_id, node_id, source["id"], kind, len(fragments))

        return self.write(run)

    def duplicate(self, node_id):
        self.note = "duplicate"
        return "%s\nnote duplicate: %s" % (node_id, self.refusal_text("duplicate", {"id": node_id}))

    def op_add_summary(self, rest):
        p = self.parser("add-summary")
        p.add_argument(self.flag("of"), dest="of", required=True)
        p.add_argument(self.flag("text"), dest="text", required=True)
        a = self.parse("add-summary", p, rest)
        text = self.text_arg(a.text, "text", "summary")

        def run():
            ev = self.node(a.of, ["evidence"])
            dupkey = json.dumps([ev["id"], text], ensure_ascii=False)
            existing = self.db.execute("SELECT id FROM nodes WHERE kind='summary' AND dupkey=?", (dupkey,)).fetchone()
            if existing:
                return self.duplicate(existing[0])
            node_id = self.insert_node("summary", text=text, dupkey=dupkey)
            self.add_relation("summarizes", node_id, ev["id"])
            return "%s\nsummary %s summarizes %s" % (node_id, node_id, ev["id"])

        return self.write(run)

    def op_add_group(self, rest):
        p = self.parser("add-group")
        p.add_argument(self.flag("level"), dest="level", required=True)
        p.add_argument(self.flag("label"), dest="label", required=True)
        p.add_argument(self.flag("in"), dest="parent")
        a = self.parse("add-group", p, rest)
        if a.level not in LEVELS:
            raise Refused("bad-argument", detail="%s takes level1, level2 or level3, not \"%s\"" % (self.flag("level"), a.level),
                          usage=self.usage("add-group"))
        label = self.text_arg(a.label, "label", "label")

        def run():
            dupkey = json.dumps([a.level, label], ensure_ascii=False)
            existing = self.db.execute("SELECT id FROM nodes WHERE kind='group' AND dupkey=?", (dupkey,)).fetchone()
            if existing:
                # The group exists; --in still places it (or is refused), never silently dropped.
                out = self.duplicate(existing[0])
                if a.parent is not None:
                    parent = self.node(a.parent, ["group"])
                    self.check_link(self.node(existing[0]), "part-of", parent)
                    if self.relation_exists("part-of", existing[0], parent["id"]):
                        out += "\n%s part-of %s was already linked" % (existing[0], parent["id"])
                    else:
                        self.add_relation("part-of", existing[0], parent["id"])
                        out += "\n%s part-of %s" % (existing[0], parent["id"])
                return out
            node_id = self.insert_node("group", level=a.level, label=label, dupkey=dupkey)
            out = "%s\n%s group %s" % (node_id, a.level, node_id)
            if a.parent is not None:
                parent = self.node(a.parent, ["group"])
                self.check_link(self.node(node_id), "part-of", parent)
                self.add_relation("part-of", node_id, parent["id"])
                out += " part-of %s" % parent["id"]
            return out

        return self.write(run)

    def three(self, op, rest):
        p = self.parser(op)
        p.add_argument("from_id")
        p.add_argument("relation")
        p.add_argument("to_id")
        return self.parse(op, p, rest)

    def check_link(self, a, relation, b):
        def not_allowed():
            raise Refused("relation-not-allowed", relation=relation, from_id=a["id"], from_kind=self.kind_name(a),
                          to_id=b["id"], to_kind=self.kind_name(b), allowed=ALLOWED)

        if relation not in LINKABLE:
            not_allowed()
        if relation in ("member-of", "part-of") and b["kind"] == "group":
            if a["id"] == b["id"] or (a["kind"] == "group" and self.inside(b["id"], a["id"])):
                raise Refused("cycle", relation=relation, from_id=a["id"], to_id=b["id"])
        if relation == "member-of":
            if a["kind"] != "summary" or b["kind"] != "group":
                not_allowed()
            if b["level"] != LEVELS[0]:
                raise Refused("level-skip", relation=relation, from_id=a["id"], from_level="summary", to_id=b["id"],
                              to_level=b["level"], next_level=LEVELS[0])
        elif relation == "part-of":
            if a["kind"] != "group" or b["kind"] != "group" or a["level"] == LEVELS[-1]:
                not_allowed()
            nxt = LEVELS[LEVELS.index(a["level"]) + 1]
            if b["level"] != nxt:
                raise Refused("level-skip", relation=relation, from_id=a["id"], from_level=a["level"], to_id=b["id"],
                              to_level=b["level"], next_level=nxt)
        elif relation == "addresses":
            if a["kind"] != "group" or b["kind"] != "question":
                not_allowed()
        elif relation == "set-aside":
            if a["kind"] not in ("summary", "evidence") or b["kind"] != "question":
                not_allowed()

    def inside(self, start, target):
        """True when target is reached from start by following part-of upward."""
        seen, todo = set(), [start]
        while todo:
            cur = todo.pop()
            if cur == target:
                return True
            if cur in seen:
                continue
            seen.add(cur)
            todo.extend(r[0] for r in self.db.execute("SELECT dst FROM relations WHERE kind='part-of' AND src=?", (cur,)))
        return False

    def link(self, a_id, relation, b_id, op):
        def run():
            a, b = self.node(a_id), self.node(b_id)
            self.check_link(a, relation, b)
            if self.relation_exists(relation, a["id"], b["id"]):
                self.note = "duplicate"
                return "%s %s %s\nnote duplicate: %s" % (a["id"], relation, b["id"],
                                                         self.refusal_text("duplicate", {"id": "%s %s %s" % (a["id"], relation, b["id"])}))
            self.add_relation(relation, a["id"], b["id"])
            return "%s %s %s" % (a["id"], relation, b["id"])

        return self.write(run)

    def op_link(self, rest):
        a = self.three("link", rest)
        return self.link(a.from_id, a.relation, a.to_id, "link")

    def op_unlink(self, rest):
        a = self.three("unlink", rest)

        def run():
            x, y = self.node(a.from_id), self.node(a.to_id)
            if a.relation not in LINKABLE:
                raise Refused("relation-not-allowed", relation=a.relation, from_id=x["id"], from_kind=self.kind_name(x),
                              to_id=y["id"], to_kind=self.kind_name(y), allowed=ALLOWED)
            if not self.relation_exists(a.relation, x["id"], y["id"]):
                raise Refused("bad-argument", detail="there is no link %s %s %s to remove" % (x["id"], a.relation, y["id"]),
                              usage=self.usage("unlink"))
            self.db.execute("DELETE FROM relations WHERE kind=? AND src=? AND dst=?", (a.relation, x["id"], y["id"]))
            return "removed %s %s %s" % (x["id"], a.relation, y["id"])

        return self.write(run)

    def op_relabel(self, rest):
        p = self.parser("relabel")
        p.add_argument("id")
        p.add_argument(self.flag("label"), dest="label")
        p.add_argument(self.flag("text"), dest="text")
        a = self.parse("relabel", p, rest)

        def run():
            n = self.node(a.id, ["group", "summary"])
            if n["kind"] == "group":
                if a.label is None:
                    raise Refused("bad-argument", detail="a group takes %s" % self.flag("label"), usage=self.usage("relabel"))
                label = self.text_arg(a.label, "label", "label")
                dupkey = json.dumps([n["level"], label], ensure_ascii=False)
                self.refuse_taken("group", dupkey, n["id"])
                self.db.execute("UPDATE nodes SET label=?, dupkey=? WHERE id=?", (label, dupkey, n["id"]))
                return "%s\n%s group %s: %s" % (n["id"], n["level"], n["id"], label)
            if a.text is None:
                raise Refused("bad-argument", detail="a summary takes %s" % self.flag("text"), usage=self.usage("relabel"))
            text = self.text_arg(a.text, "text", "summary")
            ev = self.db.execute("SELECT dst FROM relations WHERE kind='summarizes' AND src=?", (n["id"],)).fetchone()[0]
            dupkey = json.dumps([ev, text], ensure_ascii=False)
            self.refuse_taken("summary", dupkey, n["id"])
            self.db.execute("UPDATE nodes SET text=?, dupkey=? WHERE id=?", (text, dupkey, n["id"]))
            return "%s\nsummary %s: %s" % (n["id"], n["id"], text)

        return self.write(run)

    def refuse_taken(self, kind, dupkey, own_id):
        other = self.db.execute("SELECT id FROM nodes WHERE kind=? AND dupkey=? AND id != ?", (kind, dupkey, own_id)).fetchone()
        if other:
            raise Refused("bad-argument", detail="%s already has these words; link to %s or choose other words" % (other[0], other[0]),
                          usage=self.usage("relabel"))

    def op_set_aside(self, rest):
        p = self.parser("set-aside")
        p.add_argument("id")
        a = self.parse("set-aside", p, rest)
        return self.link(a.id, "set-aside", self.the_question(), "set-aside")

    # ------------------------------------------------------------ reading

    def links_out(self, node_id):
        return [(r[0], r[1]) for r in self.db.execute(
            "SELECT kind, dst FROM relations WHERE src=? ORDER BY kind, dst", (node_id,))]

    def links_in(self, node_id):
        return [(r[0], r[1]) for r in self.db.execute(
            "SELECT kind, src FROM relations WHERE dst=? ORDER BY kind, src", (node_id,))]

    def line(self, n, detail):
        out = self.links_out(n["id"])
        links = ", ".join("%s %s" % (k, d) for k, d in out if k not in ("drawn-from", "summarizes"))
        if n["kind"] == "source":
            count = self.db.execute("SELECT COUNT(*) FROM relations WHERE kind='drawn-from' AND dst=?", (n["id"],)).fetchone()[0]
            s = "%s source, %d evidence row(s)" % (n["id"], count)
        elif n["kind"] == "question":
            s = "%s question: %s" % (n["id"], n["text"])
        elif n["kind"] == "evidence":
            src = dict(out).get("drawn-from")
            # A fragment copied across a wrapped account line may hold a newline; it is shown as a space.
            if detail == "detailed":
                frags = " | ".join('"%s" [%d-%d]' % (one_line(f["text"]), f["start"], f["end"]) for f in n["fragments"])
            else:
                frags = " | ".join('"%s"' % one_line(f["text"]) for f in n["fragments"])
            s = "%s evidence from %s, kind %d: %s" % (n["id"], src, n["evidenceKind"], frags)
        elif n["kind"] == "summary":
            s = "%s summary of %s: %s" % (n["id"], dict(out).get("summarizes"), n["text"])
        else:
            s = "%s %s group: %s" % (n["id"], n["level"], n["label"])
        return s + ("  (%s)" % links if links else "")

    def node_rows(self, where, params):
        rows = self.db.execute("SELECT n.id FROM nodes n WHERE %s ORDER BY n.kind, n.seq, n.id" % where, params).fetchall()
        return [r[0] for r in rows]

    def paged(self, ids, page, detail, what):
        size = self.surface["pageSize"]
        pages = max(1, -(-len(ids) // size))
        if page > pages:
            raise Refused("bad-argument", detail="there are %d page(s) of %s" % (pages, what), usage="")
        lines = [self.line(self.node(i), detail) for i in ids[(page - 1) * size: page * size]]
        return "\n".join(lines + ["page %d of %d (%d %s)" % (page, pages, len(ids), what)])

    def op_show(self, rest):
        p = self.parser("show")
        p.add_argument("id")
        p.add_argument(self.flag("detail"), dest="detail")
        a = self.parse("show", p, rest)
        detail = self.detail_arg(a.detail, "show")
        n = self.node(a.id)
        lines = [self.line(n, detail)]
        incoming = self.links_in(n["id"])
        if incoming:
            lines.append("linked from: " + ", ".join("%s %s" % (src, k) for k, src in incoming))
        if detail == "detailed" and n["kind"] == "source":
            lines.append("sha256 %s" % sha256(n["text"]))
        return "\n".join(lines)

    def detail_arg(self, value, op):
        value = value or self.surface["detail"]
        if value not in ("concise", "detailed"):
            raise Refused("bad-argument", detail="%s takes concise or detailed" % self.flag("detail"), usage=self.usage(op))
        return value

    def op_list(self, rest):
        p = self.parser("list")
        p.add_argument("type")
        for key in ("source", "kind", "level", "in", "page", "detail"):
            p.add_argument(self.flag(key), dest=key)
        a = self.parse("list", p, rest)
        if a.type not in NODE_KINDS:
            raise Refused("bad-argument", detail="list takes one of %s, not \"%s\"" % (", ".join(NODE_KINDS), a.type),
                          usage=self.usage("list"))
        page, detail = self.page_arg(a.page), self.detail_arg(a.detail, "list")
        where, params = ["n.kind = ?"], [a.type]
        if a.source is not None:
            if a.type == "evidence":
                where.append("n.source = ?")
            elif a.type == "summary":
                where.append("EXISTS (SELECT 1 FROM relations r JOIN nodes e ON e.id = r.dst WHERE r.kind='summarizes' AND r.src = n.id AND e.source = ?)")
            else:
                raise Refused("bad-argument", detail="%s filters evidence and summaries" % self.flag("source"), usage=self.usage("list"))
            params.append(a.source)
        if a.kind is not None:
            if a.type != "evidence" or a.kind not in ("1", "2", "3", "4", "5"):
                raise Refused("bad-argument", detail="%s 1-5 filters evidence" % self.flag("kind"), usage=self.usage("list"))
            where.append("n.evidence_kind = ?")
            params.append(int(a.kind))
        if a.level is not None:
            if a.type != "group" or a.level not in LEVELS:
                raise Refused("bad-argument", detail="%s level1|level2|level3 filters groups" % self.flag("level"), usage=self.usage("list"))
            where.append("n.level = ?")
            params.append(a.level)
        group_in = getattr(a, "in")
        if group_in is not None:
            rel = {"summary": "member-of", "group": "part-of"}.get(a.type)
            if rel is None:
                raise Refused("bad-argument", detail="%s filters summaries and groups" % self.flag("in"), usage=self.usage("list"))
            if group_in == "none":
                # Not in any group; a summary also counts as placed when it is set aside.
                where.append("NOT EXISTS (SELECT 1 FROM relations r WHERE r.src = n.id AND r.kind IN (?, 'set-aside'))")
                params.append(rel)
            else:
                self.node(group_in, ["group"])
                where.append("EXISTS (SELECT 1 FROM relations r WHERE r.src = n.id AND r.kind = ? AND r.dst = ?)")
                params.extend([rel, group_in])
        ids = self.node_rows(" AND ".join(where), params)
        return self.paged(ids, page, detail, "rows")

    def op_find(self, rest):
        p = self.parser("find")
        p.add_argument("words", nargs="+")
        p.add_argument(self.flag("page"), dest="page")
        p.add_argument(self.flag("detail"), dest="detail")
        a = self.parse("find", p, rest)
        # A newline and a space are the same character here, as when a fragment is located.
        words = one_line(self.text_arg(" ".join(a.words), "text", "find")).lower()
        page, detail = self.page_arg(a.page), self.detail_arg(a.detail, "find")
        ids = []
        for r in self.db.execute("SELECT id, kind, text, label, fragments FROM nodes WHERE kind != 'source' ORDER BY kind, seq, id"):
            searched = r[2] or r[3] or " ".join(f["text"] for f in json.loads(r[4] or "[]"))
            if words in one_line(searched).lower():
                ids.append(r[0])
        return self.paged(ids, page, detail, "matches")

    # ------------------------------------------------------------ setup and export

    def init(self, rest):
        p = argparse.ArgumentParser(prog="graph.py init", add_help=False, allow_abbrev=False)
        p.add_argument("--sources")
        p.add_argument("--sources-dir")
        p.add_argument("--question", required=True)
        a = p.parse_args(rest)
        if a.sources is not None:
            with open(a.sources, encoding="utf-8") as f:
                sources = json.load(f)
        elif a.sources_dir is not None:
            names = sorted(n for n in os.listdir(a.sources_dir) if n.endswith((".txt", ".md")))
            if not names:
                raise Failure("init found no .txt or .md account files in %s" % a.sources_dir)
            sources, owner = [], {}
            for name in names:
                sid = account_id(name)
                if sid in owner:
                    raise Failure("%s and %s both give the account id %s; rename one" % (owner[sid], name, sid))
                owner[sid] = name
                with open(os.path.join(a.sources_dir, name), encoding="utf-8-sig", newline="") as f:
                    sources.append({"id": sid, "text": f.read()})
        else:
            raise Failure("init needs --sources-dir FOLDER")
        if not isinstance(sources, list) or not sources:
            raise Failure("--sources must hold a non-empty JSON array of {id, text}")
        seen = set()
        for s in sources:
            if (not isinstance(s, dict) or sorted(s) not in (["id", "text"], ["id", "personSpans", "text"])
                    or not isinstance(s["id"], str) or not isinstance(s["text"], str)):
                raise Failure("each source must be {id, text} or {id, text, personSpans} with string id and text")
            if "personSpans" in s:
                check_person_spans(s["id"], s["text"], s["personSpans"])
            if not SOURCE_ID.match(s["id"]) or GENERATED_ID.match(s["id"]) or s["id"] in seen:
                raise Failure("source id %r must be distinct, of letters, digits, '.', '_' or '-', and not shaped like e1, s1, g1 or q1" % s["id"])
            seen.add(s["id"])
        if not a.question.strip():
            raise Failure("init needs a question")
        self.db.executescript(SCHEMA)
        if self.db.execute("SELECT COUNT(*) FROM nodes").fetchone()[0] != 0:
            raise Failure("the graph is already set up in this folder; reuse it (python3 graph.py list source)")

        def run():
            for s in sources:
                spans = json.dumps(s["personSpans"]) if "personSpans" in s else None
                self.db.execute("INSERT INTO nodes (id, kind, seq, text, sha256, person_spans) VALUES (?, 'source', 0, ?, ?, ?)",
                                (s["id"], s["text"], sha256(s["text"]), spans))
            q = self.insert_node("question", text=a.question)
            return "initialised with %d source(s) and question %s" % (len(sources), q)

        return self.write(run)

    def export(self, rest):
        p = argparse.ArgumentParser(prog="graph.py export", add_help=False, allow_abbrev=False)
        p.add_argument("--out", required=True)
        a = p.parse_args(rest)
        lines = []
        self.db.execute("BEGIN")
        for r in self.db.execute("SELECT id, kind, text, sha256, level, label, evidence_kind, fragments, person_spans FROM nodes"):
            obj = {"type": "node", "kind": r[1], "id": r[0]}
            if r[1] == "source":
                obj["sha256"] = r[3]
                if r[8] is not None:
                    obj["personSpans"] = json.loads(r[8])
            elif r[1] in ("question", "summary"):
                obj["text"] = r[2]
            elif r[1] == "evidence":
                obj["evidenceKind"] = r[6]
                obj["fragments"] = json.loads(r[7])
            elif r[1] == "group":
                obj["level"], obj["label"] = r[4], r[5]
            lines.append(((obj["type"], obj["kind"], obj["id"], "", 0), obj))
        for r in self.db.execute("SELECT kind, src, dst FROM relations"):
            lines.append((("relation", r[0], r[1], r[2], 0), {"type": "relation", "kind": r[0], "from": r[1], "to": r[2]}))
        for r in self.db.execute("SELECT n, verb, args_sha256, outcome, refusal_key, at FROM calls"):
            lines.append((("call", "", "", "", r[0]), {"type": "call", "n": r[0], "verb": r[1], "argsSha256": r[2],
                                                      "outcome": r[3], "refusalKey": r[4], "at": r[5]}))
        self.db.execute("COMMIT")
        lines.sort(key=lambda x: x[0])
        body = "".join(json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n" for _, obj in lines)
        tmp = a.out + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
        os.replace(tmp, a.out)
        return "exported %d line(s) to %s" % (len(lines), a.out)

    # ------------------------------------------------------------ dispatch

    def log(self, verb, rest, outcome, key):
        if not self.tables_exist():  # help before setup: nothing to record yet
            return
        args = hashlib.sha256(json.dumps(rest, ensure_ascii=False).encode("utf-8")).hexdigest()
        self.db.execute("INSERT INTO calls (verb, args_sha256, outcome, refusal_key, at) VALUES (?,?,?,?,?)",
                        (verb, args, outcome, key, now()))

    def run_agent(self, token, rest):
        ops = {v: k for k, v in self.verbs.items()}
        op = ops.get(token)
        self.note = None
        # Set while an agent command runs: write() logs it inside its transaction and clears it; a command that writes
        # nothing (or is refused, its write rolled back) is logged here as before.
        self.call = None if op is None else (op, rest)
        try:
            if op is None:
                raise Refused("bad-argument", detail=self.no_such_command(token),
                              usage="%s %s" % (self.command, self.verb("help")))
            if op != "help" and not self.tables_exist():
                raise Failure(NOT_SET_UP)
            out = getattr(self, "op_" + op.replace("-", "_"))(rest)
        except Refused as r:
            self.call = None
            self.log(op or token, rest, "refused", r.key)
            values = dict(r.values)
            values.setdefault("usage", "")
            if not values["usage"] and op is not None:
                values["usage"] = self.usage(op)
            text = " ".join(self.refusal_text(r.key, values).split("\n"))
            print("refused %s: %s" % (r.key, text))
            return 2
        if self.call is not None:
            self.log(op, rest, "duplicate" if self.note == "duplicate" else "ok", None)
            self.call = None
        print(out)
        return 0


SCHEMA = """
CREATE TABLE IF NOT EXISTS nodes (
  id TEXT PRIMARY KEY, kind TEXT NOT NULL, seq INTEGER NOT NULL, text TEXT, sha256 TEXT,
  level TEXT, label TEXT, evidence_kind INTEGER, fragments TEXT, source TEXT, dupkey TEXT, person_spans TEXT);
CREATE UNIQUE INDEX IF NOT EXISTS nodes_dupkey ON nodes (kind, dupkey) WHERE dupkey IS NOT NULL;
CREATE TABLE IF NOT EXISTS relations (
  kind TEXT NOT NULL, src TEXT NOT NULL REFERENCES nodes(id), dst TEXT NOT NULL REFERENCES nodes(id),
  PRIMARY KEY (kind, src, dst));
CREATE TABLE IF NOT EXISTS calls (
  n INTEGER PRIMARY KEY AUTOINCREMENT, verb TEXT NOT NULL, args_sha256 TEXT NOT NULL,
  outcome TEXT NOT NULL, refusal_key TEXT, at TEXT NOT NULL);
"""


def main(argv):
    p = argparse.ArgumentParser(prog="graph.py", add_help=False, allow_abbrev=False)
    p.add_argument("--db", default=DEFAULT_DB)
    p.add_argument("--surface")
    p.add_argument("verb", nargs="?")
    p.add_argument("rest", nargs=argparse.REMAINDER)
    try:
        a = p.parse_args(argv)
        surface = load_surface(a.surface) if a.surface else check_surface(json.loads(json.dumps(DEFAULT_SURFACE)))
        graph = Graph(a.db, surface)
        if a.verb == "init":
            print(graph.init(a.rest))
            return 0
        if a.verb == "export":
            print(graph.export(a.rest))
            return 0
        return graph.run_agent(a.verb or graph.verb("help"), a.rest)
    except Failure as e:
        print("graph.py: %s" % e, file=sys.stderr)
        return 1
    except SystemExit as e:
        return 1 if e.code else 0
    except Exception as e:
        print("graph.py: internal error: %s: %s" % (type(e).__name__, e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
