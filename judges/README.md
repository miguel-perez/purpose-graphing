# The judges

These are the three judges purpose-graphing was scored with. They are published so you can see exactly what "rated 14% higher" means, check the skill's work the same way, or use the judges in your own tests.

The skill was built using Indi Young's method, Data Science that Listens, and the judges were trained on her work. The skill and its judges are not certified or endorsed by her.

## What a judge is

A judge is a set of questions. Each question has a ladder of answers, from worst to best. For example, the summary judge asks whether a summary keeps how the person's thought relates to its reason, trigger or goal. Its answers run from one that reverses or invents that relationship, up to one that conveys it faithfully.

The questions are read by Jev, a small scoring model from TypeSafe (`typesafe/jev-1.13`, used through OpenRouter at temperature 0). Jev does not write an answer. For each question it gives a probability for every rung of the ladder. The judge turns that into a score:

1. For each question, take the expected rung: the average position on the ladder, weighted by Jev's probabilities.
2. Scale it to run from 0 (the bottom rung) to 1 (the top rung).
3. Average the scaled values across the questions that count toward the score.

So a score of 0.8 means that, across its questions, the judge placed the work about four fifths of the way up the ladders.

None of the questions were written by hand. Each judge was found by its own automated search, which rewrote the questions over many rounds and kept the versions that agreed best with Young's own work. The chosen version was then checked once on a separate set of material the search had never been chosen on. Each judge then passed its own checks before it scored the skill. The main README's Evidence section has the results of those checks.

## The three judges

| File | Judge | What it reads | Questions | Counted in the score |
|---|---|---|---|---|
| [summaries.json](summaries.json) | Summaries | A quote from an account and one summary of it | 9 | All 9 |
| [rows.json](rows.json) | Picking out rows | One passage picked out of an account | 14 | 1: whether the passage is the person's own thinking at the time |
| [grouping.json](grouping.json) | Grouping | A proposed group, or a link between groups, with the summaries it rests on | 3 | All 3 |

**Summaries.** It asks whether the summary names the person's own thinking or choice and what it concerns, and keeps its reason, trigger or goal. It also checks that the summary keeps the person's certainty and scope, adds nothing they did not express, and holds one thought rather than two. Finally, it checks that the summary leads with a verb, speaks in the person's present voice, and says it plainly.

**Picking out rows.** Only its first question counts: whether the passage is the person's thinking, feeling or personal rule at the time. The other 13 questions sort the passage further: into circumstances, views about a topic, habits, imagined situations and so on, and by whether it is told from inside the moment. They are recorded but enter no score, because only the first question passed its checks.

**Grouping.** It asks how well the summaries support the proposed group, how consistently they back it, and how directly they justify the interpretation the label makes. It catches labels that add a purpose the members do not share and groups wrongly split. It catches wrongly merged groups only about half the time, which is not shown to be better than chance. It was checked on small, self-contained cases, not on whole maps.

## The files

Each file holds:

- `name`: the judge;
- `questionSetHash`: an identifier for this exact set of questions;
- `scoredWith`: the model and settings;
- `reads`: what the judge is shown;
- `scoredQuestions`: the questions that count toward the score;
- `recordedOnly`: outputs that are recorded but not scored;
- `scope`: the limits of what the judge was checked on;
- `questions`: every question, each with its key, its instructions and its ladder of answers from worst to best.

## Using them

To score work the way the skill was scored, send each question with the material it reads to Jev through OpenRouter, and turn the probabilities into a score as above. The questions work as written. What changes from one use to another is the material you show them.

A score is a measurement under these questions, not a verdict on whether an interpretation is right. Read the work itself before relying on a number.

## Licence

The judges are licensed under CC BY 4.0, like the skill's text.
