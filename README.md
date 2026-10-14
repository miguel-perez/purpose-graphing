# purpose-graphing

An agent skill that reads people's own accounts of what they did and went through, and finds the patterns across them: the inner thinking, emotional reactions and guiding principles behind what people do, grouped by purpose. It is built using Indi Young's method, Data Science that Listens, and keeps every pattern traced to the words people actually said.

- **Findings you can trust.** It does the close reading one person at a time, and traces every pattern to the words behind it.
- **Findings people act on.** It finds patterns across people, carried in their own words rather than as your opinion, and keeps the analysis so you can retell it for each audience and answer the next question without starting over.
- **Your part stays yours.** It takes on the slog of the reading. The sessions and the judgement stay with you.

## Does it work?

The skill was not written by hand. It was found by an automated search and scored by judges trained on Young's own summaries, highlighted rows and groupings, on material the search was never chosen on. The same agent ran the same tasks with the skill and without it:

- **Summaries were rated 14% higher** with the skill than without it.
- **Picking out the rows to work from was rated 20% higher.**
- **Grouping came out the same** with or without the skill. It is the least proven part.

Each rating is a judge's score from 0 to 1: the average of its answers to checks, such as whether a summary keeps the person's reason and adds no motive they never expressed. A gain only counts when it is bigger than twice the normal variation between runs.

The scores come from one agent on Young's material; see [Scope and limits](#scope-and-limits). The full evidence is in [Evidence](#evidence) below.

## Install

**Claude Code**

```
/plugin marketplace add miguel-perez/purpose-graphing
/plugin install purpose-graphing@purpose-graphing
```

**Claude Code, OpenCode and the other agents the skills installer supports:**

```
npx skills add miguel-perez/purpose-graphing
```

**Claude.ai and the Claude desktop app.** Download `purpose-graphing.zip` from the [latest release](https://github.com/miguel-perez/purpose-graphing/releases/latest). Then open Settings → Capabilities → Skills and upload it.

**By hand.** Copy `skills/purpose-graphing/` into your agent's skills folder, for example `~/.claude/skills/`.

There is nothing else to install. The skill's two scripts are plain Python that use only the standard library. In Claude.ai and the desktop app they run in Claude's own code environment; turn on code execution in settings if it is off. We have checked the zip's layout but not yet run the skill in Claude.ai itself. In Claude Code, OpenCode and other agents on your computer they use your Python 3.9 or later, which most Mac and Linux machines already have. On Windows, install Python first.

## Using it

1. Put the accounts in one folder, one file each (`.txt` or `.md`). Transcripts, diary entries and written stories all work. Speaker labels are optional; the skill marks turns itself when they are missing.
2. Ask your question in your own words, and say where the accounts are. For example: *"I've got 12 interviews with nurses in sessions/. What gets in the way of handovers between shifts?"*
3. The agent loads the skill, sets up a graph in the study folder, gives each account to a helper and groups across accounts in three levels. It then writes the report under `reports/`, with `groups.csv`, `summaries.csv` and `rows.csv` beside it.

You can also use one step on its own: summarize a single quote, pick out the rows of one account, or group a set of summaries you already have.

## Findings you can trust

Turning conversations into findings is slow, and it is easy to get wrong:

- **Capture costs you hours, or fades.** Without a note-taker you rewatch every recording, or trust a memory that is gone in a week or two.
- **The volume lands on you.** Working through the material alone turns into days of wondering whether a thousand notes will ever come together.
- **Meaning slips.** It is easy to take what people say at face value, or to miss what they never say outright.

purpose-graphing does the close reading for you, one person at a time, and keeps three layers apart and linked:

- **Rows.** The person's exact words, sorted into moments of inner thinking, settled views and circumstances. Nothing is paraphrased.
- **Summaries.** One first-person sentence per moment, keeping what they thought or felt and why. A summary adds no motive the person never expressed.
- **Groups, in three levels.** Summaries from different people are joined by shared purpose, not shared topic. Those groups are grouped again, and again at the top.

No layer may say more than the layer beneath it supports, and every link is stored, so you can check any pattern against the words behind it.

### An example from our own research

We ran the skill on our own interviews with UX researchers about how they turn sessions into findings. One question was *"How do researchers get their findings acted on?"* Below is one account, adapted from those interviews and reworded, with details changed so no sentence is anyone's actual words. After it is what the skill does with it.

> "Our last readout was on why people stop rating the restaurants they order from. I've learned that if I just stand up and present our results, the product team hears it as the research team's opinion. So this time I opened with a short clip of one customer explaining why she gave up after we hid a rating she'd left. I wanted them to hear it from her, not from me."

**Step 1: rows.** The skill reads the whole account and picks out what the person said, in their exact words, sorted by what each passage expresses:

| Row | What it expresses |
|---|---|
| "Our last readout was on why people stop rating the restaurants they order from." | a circumstance |
| "if I just stand up and present our results, the product team hears it as the research team's opinion" | a settled view, not tied to one moment |
| "this time I opened with a short clip of one customer explaining why she gave up after we hid a rating she'd left. I wanted them to hear it from her, not from me." | a moment of inner thinking: a decision and its reason |

**Step 2: summaries.** For the moment of inner thinking, it writes one sentence in the person's own voice that keeps what they decided and why:

- *Open the readout with a customer explaining why she gave up, so the team hears it from her rather than from me.*

**Step 3: groups across people.** It does the same for every other interview, then looks for summaries from different people that serve the same purpose. Two other researchers gave these, also reworded:

- *Put participants' own quotes and clips in the deck, so the team agrees with the person struggling instead of taking my word for it.*
- *Lay out the broken process step by step, so the stakeholders feel the pain and no team can shrug it off.*

The three do different things: a clip, quotes in a deck, a process diagram. They share a purpose, so the skill groups them under *Let stakeholders feel the problem for themselves, so a finding is not taken as my opinion*. Together with other groups, that becomes part of the answer to the question, with each person's words kept beside it.

## Findings people act on

Your findings only matter if the people who decide, build and sell act on them. Stated in your own voice, a finding can be heard as your opinion. One striking remark can be mistaken for a theme. And turning a wall of notes into something you can share takes days.

purpose-graphing helps you get findings across:

- **It counts people, not remarks.** It keeps the differences and counterexamples, so one person's comment does not pass for a pattern.
- **It puts participants' own words behind every pattern,** so a finding is not just your word against someone else's.
- **It writes a report** that answers your question, with the circumstances behind each pattern.
- **It writes CSV tables.** `groups.csv` holds every group with its level and parent. `summaries.csv` holds each summary with its three levels of groups side by side. `rows.csv` holds every row. Every line names its study. All three are ready for a spreadsheet, a whiteboard, a deck or a BI tool.

It does not make stakeholders read, and it does not produce the large numbers some leaders ask for. Those stay with you.

### The analysis outlives the report

A report answers one question for one audience. The skill also keeps the analysis itself: every row, summary and group, linked to the words behind it, in a graph file in your study folder and in the CSV tables. Nothing that didn't fit the first question is thrown away, because every account was read in full. That means you can:

- **Retell it for each audience.** Ask your agent for a one-page brief for leaders, a deck for the product team, or the evidence behind one decision for the engineers. Each is drawn from the same groups and the same words, so the stories agree.
- **Answer the next question without starting over.** When a new question comes up months later, ask it in the same study folder. The agent works from the recorded rows, summaries and groups instead of reading every account again, and writes a new report.
- **Take it into other tools and methods.** The graph is an ordinary SQLite database, and the CSV tables open in any spreadsheet and import into whiteboards, research repositories or analysis tools. Every line carries a summary's three levels of groups and the person's exact words, so the trail survives wherever the work goes next.
- **Build a research repository from many studies.** Every line of the tables names its study, so the tables from many studies stack into one place. That could be a spreadsheet, a database, or a BI tool such as Tableau, Power BI or Looker, where people's purposes sit beside your usage and revenue metrics and every pattern still links to the words behind it.
- **Stand one up from past research.** Point the skill at the transcripts of studies you have already done, one folder per study. Each becomes a graph and three tables, so years of interviews that live only in old decks and recordings become something you can search and filter.

- **Find patterns across studies.** Give the agent the combined summaries from several studies and ask it to group them. It runs the same grouping across all of them, in three levels, so a purpose that keeps coming up in study after study shows itself, still traced to each person's words. This works best when the studies share a purpose. Patterns emerge across people pursuing the same purpose, and mixing unrelated purposes tends to produce groups by topic.

We have tested whole studies from accounts to report. Retelling for different audiences, answering follow-up questions, combining studies and grouping across them are ways to use the same files and the skill's own steps, and have not been tested as steps of their own.

## Your part stays yours

You may have to defend research to people who doubt it. And the parts that make the work worth doing are usually the sessions themselves and seeing research land, not the hours of reading in between.

purpose-graphing takes on the close reading and leaves the rest with you:

- **The sessions stay yours.** It reads transcripts; it does not sit between you and the people you listen to.
- **The judgement stays yours.** Read the rows behind any pattern before you rely on it. You remain responsible for the interpretation.
- **You can defend using it.** Its evidence and limits are published below.

**Keep your hand in.** There is a well-known pattern with automation, sometimes called the ironies of automation: when a tool takes over the routine part of a job, people are left with the hard cases while getting less practice at the work that made them good at those cases. It happens to anyone, and it is not a reason to avoid the tool. A simple counter is to keep doing some of the reading yourself. Now and then, take an account or two and pick out the rows, write the summaries and group them by hand, then compare with what the skill produced. You keep your eye sharp, you learn where the skill goes wrong, and your hand-made analysis is exactly what we need to train and test the next version. If you can share it, see [Contributing](#contributing).

It does not help with recruiting or scheduling, or with recording and transcription. It will not settle organisational politics either, though you can point it at your own interviews with stakeholders to understand what the people around a decision are trying to do.

## Why listen this way

Most product decisions rest on what people say they want: feature requests, ratings, survey scores, opinions about a screen. Those shift with every new product. What people are trying to accomplish, and what goes through their minds as they do it, shifts slowly. Indi Young's method listens for that, and it gives each role something concrete:

- **Product managers** see which purposes people pursue and which ones the product does not support yet, instead of a ranked list of requests.
- **Engineers** see why a fix matters to the people who hit the problem, in their words.
- **Designers** see the different ways people think through the same goal, so one design can serve more of them.
- **Researchers** get the close reading done consistently and traceably, ready to check and build on.

## Compared with other methods

Indi Young has written about how her method sits beside the two that most teams already know. Her position, with her own words in quotation marks:

### Jobs to be done

On her [method page](https://indiyoung.com/method), Young says that in good hands jobs to be done can reach an understanding as deep as her own method. Her concern is how it is usually applied:

- to map a process or a purchase, rather than the purpose people are pursuing;
- with only a light treatment of emotional reactions and personal rules;
- grouping people by their role in the process, not by how they think.

In hurried contexts, she writes, it "tends to circle back to the same old 'functional specification' that we started with in software design." She also cautions against starting from a job map, guessing the parts of a purpose from the top down: you can only guess a few, and only from your own point of view. Her method builds the patterns from the bottom up, out of what people actually said. She points to practitioners who began with listening sessions and a mental model skyline, then used them to write a sharper jobs-to-be-done survey.

### Personas

Young's argument, set out in [Where Do the 3 Concept Types Come From?](https://medium.com/inclusive-software/where-do-the-3-concept-types-come-from-99a00c2a4edd), is that "core cognition is tied to topics within a purpose, not to the whole person." The same person thinks differently in different circumstances, so a portrait of a type of person, with a personality, demographics and a photo, misses how people actually think. In place of personas she builds **thinking styles**: archetypes with no photos or demographics, each a different approach to the same purpose. They are drawn from patterns across people, and anyone can move between them as their circumstances change. Demographics come in only when they shape the thinking itself, as discrimination, physiology or culture can.

### Where this skill fits

purpose-graphing does the groundwork both comparisons depend on: people's inner thinking, emotional reactions and guiding principles, grouped by purpose from the bottom up and traced to their words. It does not yet build thinking styles, write a job map or run a survey. Its groups are the material those start from.

## Compared with other tools

Whatever you use, you are trading time, money and quality.

| Approach | Time | Money | Quality |
|---|---|---|---|
| Affinity mapping by hand, with sticky notes or a whiteboard | Days to weeks for one person | Your time | Your own judgement, at its best on a small set. Attention thins as the set grows, so later transcripts rarely get the reading the first ones did. |
| Asking a chat assistant to summarise the transcripts | Minutes | A subscription you may already have | Themes that tend to follow topics and the loudest opinions, with no trail back to who said what. Long sets are often cut down to fit. |
| Tagging in a research repository (Dovetail, Condens, EnjoyHQ and similar) | Faster to find things; the interpreting is still yours | Usually a per-seat subscription | As good as your tags, which usually name topics, and limited to what you tag. |
| Sentiment analysis and topic clustering | Fast at any scale | A tool or a data team | Groups by words or tone, not by what people were trying to do. |
| **purpose-graphing** | Runs while you do other work, with one helper per account in parallel | No extra licence: model calls in the agent you already use | Every account read in full, with each pattern traced to the words behind it. Rated against Young's own work: summaries 14% higher and row picking 20% higher than the same agent without the skill; grouping the same. |

**A different way of working.** The skill does not get tired and does not skim. Each account gets its own helper and the same complete reading, so a large set of interviews is read as carefully as a small one. The reading on our own research (22 recorded conversations, about 148,000 words) ran in one sitting. The first pass becomes something you review rather than something you grind through, and you keep the judgement about what the patterns mean.

Only the quality comparison with a plain chat assistant was measured. The time and money columns describe how each approach usually works; we have not timed or costed the skill against doing the work by hand.

## Evidence

How the skill was made and tested, what the tests found, and what changed afterwards.

<details>
<summary><b>How the skill was made</b></summary>

A proposer model drafted the whole skill folder from a plain statement of the goal. An evolutionary search ([GEPA](https://github.com/gepa-ai/gepa)) then revised it over many rounds, keeping changes that scored better. The scores came from three judges, each a set of questions read by Jev, a small scoring model from TypeSafe (`typesafe/jev-1.13`). Jev gives a probability for every possible answer instead of writing one, which makes its scores steady from run to run. Every candidate ran as an installed skill in a real coding agent (DeepSeek V4.1 Flash in OpenCode), loaded through the agent's own skill mechanism, never pasted into a prompt.

The search chose its folder on one set of material. It was then read once on a separate confirmation set it had never been chosen on. The figures here are from that confirmation read.

</details>

<details>
<summary><b>The judges, and how they were checked</b></summary>

Each judge is a set of questions read by Jev, a small scoring model. Each judge was trained by its own search and passed its own checks before it scored any skill. All three are published in [judges/](judges/), with every question, how a score is computed, and what each judge was checked on.

- **Summaries.** It was checked on whether it prefers Young's summaries over damaged versions of them and over summaries written by models with no skill. On 786 held-out pairs it agreed 93% of the time, against 90% for a hand-written question set. It caught deliberately planted faults 96% of the time: a summary cut short, reported speech, past tense, two thoughts at once.
- **Picking out rows.** It was checked on whether it places passages inside or outside a person's inner thinking as Young does. On Young's own highlighted rows it agreed 81% of the time, against 58% for its starting point. Everything it called inner thinking was inner thinking, and it found 92% of what Young kept.
- **Grouping.** It was checked on cases where a correct grouping sits beside damaged ones. It catches a label that adds a purpose the members do not share 93% of the time, and a group wrongly split 91% of the time. It catches a wrongly merged group only 51% of the time, which is not shown to be better than chance. This matters for the grouping result.

</details>

<details>
<summary><b>Full results, with and without the skill</b></summary>

Running the same agent twice gives slightly different results. We ran it six times without the skill to measure that variation, and counted a gain only when the skill beat the no-skill score by more than twice the variation.

| Task | With the skill | Without | Difference |
|---|---|---|---|
| Summarizing single quotes (180 runs) | 0.818 | 0.717 | 14% higher |
| Picking out rows from an account (63 runs) | 0.542 | 0.452 | 20% higher |
| Picking out rows, summarizing and grouping in one task (36 runs) | 0.653 | 0.514 | 27% higher |
| Grouping summaries (48 cases, 3 passes) | 0.768 | 0.766 | the same |

The first three cleared the bar for a real gain. The bars were 0.724 for summaries, 0.471 for rows and 0.546 for the combined task. Grouping did not clear it.

**Grouping did not beat the agent without the skill.** It would have needed 0.788. Because the grouping judge cannot reliably tell a wrong merge from a right one, a gain could not be shown. So a different rule was set for grouping before this read: it passes if it beats both trivial groupings (everything in one group scores 0.205, every summary on its own 0.691) and does not drop below the no-skill agent by more than twice the variation between runs. Compared case by case:

- overall it was level, +0.001 (90% interval −0.031 to +0.034);
- on one family of cases it was slightly ahead, +0.022 (90% interval +0.001 to +0.044);
- on a family of people held back from all training it was −0.020, within the allowed drop (90% interval −0.083 to +0.043).

**Whole studies.** The skill was also given 12 whole studies, each a set of accounts and a question to answer in a report. All 12 finished, covered every account and delivered a report, each keeping its work in the skill's graph with no failures. Studies are judged on finishing only, because no qualified reader of study reports exists yet.

**Loading.** The skill loaded on every summary and row-picking task, on 140 of 144 grouping runs and on 33 of 36 combined tasks. A run that did not load it was scored on its output as it stood.

</details>

<details>
<summary><b>When the skill loads</b></summary>

A fixed set of 176 requests, some calling for the skill and some not, was sent to the agent with the skill installed (DeepSeek V4.1 Flash in OpenCode):

- **Requests it is for:** it loaded on every one.
- **Requests it is not for:** it stayed unloaded on 92%, 100%, 75% and 100% of them across the four parts of the set. The folder as tested, under its lab name, scored 83%, 75%, 75% and 75%.
- **The right part of the skill for the request:** chosen 94%, 86%, 83% and 97% of the time.

That is one run each, so it shows the new name and description did no harm, not that they helped. These checks ran under the name experience-graphing; the skill was renamed purpose-graphing afterwards, with its description unchanged.

In Claude Code, run headless with two turns, it loaded on 10 of 12 informal requests it is for and on none of the 12 it is not for. Of the two misses, one loads when given more turns. The other asks for files the request mentioned but did not attach.

</details>

<details>
<summary><b>A reading on real research</b></summary>

As a final check, the released skill was run once in Claude Code (Claude Opus 5.5) on our 22 recorded conversations with UX researchers and product people. The request asked how UX researchers work and where synthesis and stakeholder communication hurt.

- **Setup:** the skill set up its own study folder.
- **Rows and summaries:** one helper per conversation loaded the skill itself and recorded that conversation's rows and summaries, 2,062 rows and 464 summaries in all.
- **Groups:** 60 groups under 11 broader ones, with 24 summaries set aside as remarks about the recorded conversation itself and nothing left unplaced. The top level of 3 was added after the report.
- **Report:** the skill delivered a report. The three concerns this page is built around, trustworthy findings, findings acted on, and keeping the work worth doing, are the three broad patterns it found.

The reading was not scored, and the person running it had seen an earlier summary of the same research. It shows the skill working end to end on material from outside Young's studies; it does not measure quality.

</details>

<details>
<summary><b>What changed after testing</b></summary>

After evaluation, the skill was renamed, given a setup step and lightly reworded for use outside the lab; its analysis instructions are as confirmed, except that a whole study must now build all three levels of groups.

- **Name and description.** The name changed from account-meaning-study to experience-graphing, and then to purpose-graphing, and the description was rewritten to say what the skill finds. The final reading and the loading checks ran under the name experience-graphing.
- **Setup.** A setup step was added. It copies the scripts into a study folder, puts each account in its own file, marks speaker turns where they are missing, and starts the graph. In testing, the test harness did this.
- **Wording.** Wording that assumed every account is a conversation now says account: "the whole account" instead of "the whole conversation", and "filler" instead of "conversational filler". Two other lines were reworded without changing their sense: the instruction to summarize only the quotes supplied, and the instruction to inspect every summary, following pagination.
- **Loading line.** A line about loading the skill afresh in each session became the rule that each helper loads it through its own skill tool.
- **Report location.** The report goes under `reports/` unless the request names another place.
- **Graph script.** It now carries its configuration inside it, sets up a study from a folder of accounts, and works without the test harness. Every message it prints is unchanged.

Two more changes came after the reading on real research, so that reading used neither:

- **A CSV export.** `scripts/export_csv.py` writes the graph out as the three tables described above, each line naming its study. It reads the graph and changes nothing in it.
- **Three levels of groups in every whole study.** The tested text let a whole study stop at fewer levels, and the reading stopped at two until its third level was added afterwards. The skill now requires all three. This changes three sentences of the confirmed grouping instructions and adds one more, saying the rule takes precedence over the graph script's own help, which still says to build only useful levels because the script is kept exactly as tested. The skill was not scored again after this change.

The released text was checked for copied passages: no run of eight or more words is shared with Young's quotes and summaries.

</details>

## Scope and limits

- **It is for first-person accounts** of people pursuing a purpose: what they did, thought and felt, in their own words. It is not for surveys, support tickets, analytics or opinions about a feature list.
- **It was tested on Young's material.** Every score comes from accounts in Young's published studies and course material, and every person in her performance study was seen by the search or its judges. The clearest unseen test is a family of people held back from all training, read for grouping.
- **It was scored with one agent,** DeepSeek V4.1 Flash in OpenCode. In Claude Code it has been loaded and run end to end, but not scored.
- **The scores come from judges, not people.** The judges were checked against Young's work. No person read the skill's output blind as part of these tests.
- **Grouping is unproven.** It came out level with the agent working without the skill, and the grouping judge cannot reliably spot a wrong merge.
- **Time saved has not been measured.**

## Contributing

The skill's text is not edited by hand. It was found by search and tested, so changes go back to the lab, get tested there, and come out as a new release. You can help in three ways:

- **Report a bug** in an issue: what you asked, what happened, and your agent, model and Python version.
- **Suggest an improvement** in an issue, ideally with an example of a summary or group you think is wrong.
- **Offer data for training and testing:** accounts, ideally with your own analysis of them, and consent that covers this use. Open a data-offer issue describing it, and we will arrange a private way to send it.

Never put participants' words or files in an issue; issues are public. [CONTRIBUTING.md](CONTRIBUTING.md) has the details.

## Credit and licence

purpose-graphing was made using Indi Young's method, Data Science that Listens, with her data used to train and evaluate it. It is not certified or endorsed by her. To learn the method itself, see [indiyoung.com](https://indiyoung.com).

The skill's text is licensed under [CC BY 4.0](LICENSE). The two scripts, `skills/purpose-graphing/scripts/graph.py` and `export_csv.py`, are licensed under the [MIT licence](LICENSE-CODE).
