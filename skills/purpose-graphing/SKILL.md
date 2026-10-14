---
name: purpose-graphing
description: "Finds what went through people's minds in their own accounts, and the patterns across people: exact rows from an account, first-person summaries of single quotes, and groups of summaries by shared purpose. Use for a whole study of several accounts, such as transcripts of recorded sessions or calls, diary entries, or written stories of something people did, keeping the evidence in a graph and writing a report; or for one step alone, even a single short quote, a motivation or a feeling."
---

# Purpose graphing

Keep the person's words, their supported meaning, and the meaning shared across people distinct. Preserve the connections between them. Neither invent missing thinking nor discard expressed thinking merely because it is informal, brief, or mixed with background.

## Read the file for the task

- **Rows from an account:** read [Extracting rows](references/highlight.md).
- **A summary of a quote:** read [Summarizing a quote](references/summarize.md), even for a short quote or a quote supplied after extraction.
- **Grouping supplied summaries:** read [Grouping by meaning](references/map.md).
- **Rows followed by summaries:** read the row instructions for extraction, then the summary instructions when the quotes arrive. Summarize the quotes supplied, not passages remembered from the account.
- **A whole study:** read all three files as their tasks begin. Helpers read the files for their assigned tasks.

Each helper must load this skill through its own skill tool.

The current request governs delivery. This skill governs the substance of the work.

## Distinctions that govern the work

Rows belong to five groups:

- **Mind at a particular past moment:** the person's thought, perception, deliberation, intention, decision, or emotional response in a specific experience. Include a personal decision rule when the person describes it operating in that experience.
- **Mind-like material without a particular past moment:** hypothetical thinking, imagined future reactions, thinking spread across occasions without a particular experience, or an apparent but unstated mental state. Preserve what is said without supplying the implied thought.
- **Relationship to a topic:** standing likes, dislikes, approval, disapproval, views, or habits that are not being described as a response or guide in the particular experience.
- **Circumstances:** actions, events, surroundings, facts, and explanations of processes without an expressed mental response.
- **None of these:** material outside those meanings.

### Classify in context, not by grammar

A moment need not have a date or a phrase announcing a thought. The surrounding account can establish the experience. Present-tense words, a remembered remark, a brief evaluation, or a general-sounding rule can express what mattered then.

Distinguish these cases carefully:

- A standing preference alone describes a relationship to a topic.
- That preference explicitly explaining a particular choice can be part of the person's motivation at that moment.
- An evaluation of a particular experience can express their response, rather than a timeless opinion.
- Discovering or recognizing something can be a mental act without an emotion.
- An action alone does not establish its motive.
- A hypothetical example does not become a remembered experience merely because it sounds vivid.

Use context to understand the words, not to invent a missing cause. Before treating a passage as general background, check whether it explains the choice, expectation, feeling, or rule in the experience under discussion.

### Preserve a complete unit of meaning

One row holds one thing, not necessarily one sentence. Keep enough of the person's words to identify the thought, its object, and the expressed reason or circumstance. A tiny fragment with an unresolved “it” or “that” may lose the meaning needed for a faithful summary.

Combine separated fragments that elaborate the same thing. Separate different mental acts even when they serve a common purpose. Remove verbal clutter without stripping away the explanation. Do not copy the listener's words into a row.

For a summary, state the mental act rather than narrating the person's behavior. Use the speaker's first-person perspective and present tense, beginning with a thinking or feeling verb. For emotion, use “Feel” followed by the emotion, or a verb such as “Worry.” Preserve the object and the supported reason; do not substitute commentary about the speaker.

For grouping, compare what the people are doing mentally and what matters to them. Neither a common topic nor a matching emotion word is sufficient. Different emotion words may express the same response; similar words may express different concerns.

## Whole-study workflow

### 1. Set up the study folder

Work in a folder for the study. If it has no `graph.py` and `graph.db` yet:

1. Copy `scripts/graph.py` and `scripts/export_csv.py` from this skill's folder into the study folder.
2. Put each account in its own `.txt` or `.md` file in one folder, with nothing else in it. A file's name becomes its account's identifier.
3. If an account records people talking and its turns are not marked, write a marked copy instead: each turn on one line, starting with `Person:` for the person giving the account or `Listener:` for anyone else. Join a turn's lines into one; change no words.
4. From the study folder, run `python3 graph.py init --sources-dir FOLDER --question 'QUESTION'`, with the person's question in their own words.

If the study folder already has its graph, reuse it and do not set up again.

### 2. Establish scope and identifiers

Read the question. Identify every account registered in the graph. The question guides the report, but does not justify omitting unrelated rows from the accounts.

In the study folder, run `python3 graph.py help`. Run the graph rather than reading its program or anything under `scripts/`. The help defines command arguments and the values for recording the five row groups.

Run `python3 graph.py list source` and `python3 graph.py list question`. Reuse the returned identifiers. Do not invent account identifiers or register accounts again.

### 3. Keep account work bounded

For one account, work directly. For multiple accounts, prefer one bounded account assignment per helper when helpers are available. Avoid accumulating every full account in the parent's input.

Each helper must load this skill through its own skill tool before substantive work. Describe its assignment in your own words: task, account location, question, graph location, and responsibility boundaries. Do not paste skill text into the assignment.

Assign each account one owner for rows and summaries. Helpers record completed work in the graph. Request a compact handoff with account identifiers, recorded entry identifiers, important findings and exceptions, uncertainties, and unfinished work. The parent owns cross-account grouping and the report.

### 4. Extract and record a complete account

Read the whole account before finalizing its rows. Apply the row instructions across all five groups, not only to passages that seem useful for the report.

Before recording, make a second pass for easily missed mental content:

- brief reactions and evaluations of the experience;
- remembered decisions or remarks;
- expectations, discoveries, and changed views;
- reasons for acting or declining to act;
- preferences or personal rules explicitly explaining that choice;
- later fragments that complete an earlier explanation.

Do not automatically promote these passages. Check that their connection to the experience is supported.

Record each row with `add-evidence`, its account identifier, the kind specified in help, and a separate text argument for every exact fragment. Keep fragments in the account's order. If wording recurs, select the intended occurrence rather than altering the words.

For each row about a particular past mental moment, read the summary instructions and record a summary with `add-summary`. Write from the stored fragments. If the row has lost its object or explanation, repair the extraction before attempting to compensate in the summary.

Do not reject a quote merely because its thinking is expressed as interest, a reason for attending, a realization, or a brief decision. Equally, do not invent an intention from a bare event. If a row genuinely cannot support a mental summary, retain it, set it aside, and keep a reason for the audit.

Finish an account's rows and summaries before proceeding where practical. Resolve graph refusals from the account and the help. A duplicate response supplies an existing identifier to reuse.

### 5. Group completed summaries without leaving a backlog

Apply the grouping instructions to recorded summaries. Begin with close shared meanings. Compare each newly completed account with existing groups, revising memberships and labels as necessary. Do not postpone every membership until the end.

Create groups using `add-group`. Connect summaries with `member-of`, connect adjacent group levels with `part-of`, and connect question-relevant groups to the question using `addresses`. Build all three levels the graph allows: level1 groups of summaries, level2 groups of level1 groups, and level3 groups of level2 groups.

For each proposed group, ask what every member shares beyond vocabulary or subject matter. For each pair of neighboring groups, ask what substantive distinction justifies keeping them separate. Merge a merely verbal distinction; preserve a difference in mental orientation, concern, condition, or intended outcome.

A label must describe all members without adding a motive. Broader labels must express a genuine shared meaning, not simply name a topic or list their child labels. Each level should hold several groups that differ in meaning; do not wrap everything at one level in a single container group.

Aim to place every supported summary. A meaningful singleton is preferable to a forced match, but first compare it with the other groups. Set aside only for a substantive reason, keeping that reason for review.

### 6. Audit the graph

Use filtered lists and targeted `show` commands, following pagination:

- Every account has rows covering all of it, not just a few prominent passages.
- Context-linked mental content has not been systematically relegated to preferences or circumstances.
- Rows preserve complete meanings without combining distinct thoughts.
- Every row about a particular past mental moment has a faithful summary or a documented exception.
- Every summary has a suitable group or an explicit set-aside reason.
- Labels fit every member, and sibling boundaries reflect meaningful differences.
- Links use permitted kinds and adjacent levels.
- Question-relevant groups connect to the question.

The unplaced filter excludes entries already set aside; inspect those decisions separately. Use `relabel` to correct summaries or labels, and `unlink` followed by `link` to repair memberships. Check stored work rather than relying on remembered command success.

### 7. Write a self-contained report

Save the report under `reports/` in the study folder unless the request names another place. Answer the question directly. The reader receives the report, not the graph or the accounts.

Build the report from the supported findings, with concrete details that let the reader understand what happened and why it mattered. Include relevant conditions, constraints, choices, outcomes, differences between people, and counterexamples. Group labels alone are not findings.

Use factual rows for context, without turning them into evidence of an unspoken motive. Distinguish events reported by the person, their interpretation, and your cross-account synthesis. Ground substantive claims in identifiable accounts and, where useful, short exact fragments.

Do not mistake multiple rows for multiple people. Avoid population claims from a small set of accounts. State uncertainties where the accounts leave something unresolved.

Check the completed report against the original question and the evidence, not only against the group labels. Ensure that details needed to answer the question have survived abstraction. Keep internal coordination notes out of the report the person receives.

Then run `python3 export_csv.py` in the study folder. It writes `reports/groups.csv`, `reports/summaries.csv` and `reports/rows.csv`, with every summary's three levels of groups side by side. Tell the person these files are there.
