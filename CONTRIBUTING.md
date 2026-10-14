# Contributing

Thank you for helping. This repository works a little differently from most, so please read this before opening a pull request.

## The skill is not edited by hand

The text of the skill (`SKILL.md` and the files in `references/`) was found by an automated search and tested against judges trained on Indi Young's own work. The README explains how that testing worked. A change made by hand, however sensible it looks, would no longer be the version those results describe.

So pull requests that edit the skill's text are not merged. Instead, tell us what went wrong or what you would like, in an issue. We take it back to the lab where the skill is built, test the change there, and release a new version with its own results and a note of what changed.

The two scripts, `scripts/graph.py` and `scripts/export_csv.py`, are ordinary code under the MIT licence. A pull request that fixes a bug in them is welcome as a proposal. It will be applied and tested in the lab and released from there, with credit to you.

## Report a bug

Open an issue with the **Bug report** template. The most useful reports say:

- which agent and model you used (for example Claude Code with Claude Opus, or OpenCode with DeepSeek V4.1 Flash), and your operating system and Python version;
- what you asked for, in your own words;
- what happened, with the exact command and any error message from `graph.py` or `export_csv.py`;
- what you expected instead.

**Never paste participants' words, names or files into an issue.** Issues are public. If the problem only shows up with your data, describe it in general terms, or make up a short account that shows the same problem.

## Suggest an improvement

Open an issue with the **Suggestion** template. Tell us what you were trying to do, where the skill fell short, and what would have helped. Examples of summaries or groups that you think are wrong are especially useful. Make them up or reword them so they hold no real participant's words.

## Offer data for training and testing

The skill gets better when it is trained and tested on more people's accounts, especially alongside the analysis a careful researcher did by hand. If you have material you can share, we would like to hear from you.

What helps most:

- first-person accounts, such as interview transcripts, diary entries or written stories, of people describing something they did or went through;
- your own analysis of them, if you have it: the passages you picked out, your summaries and your groupings;
- consent from the people in them that covers use for training and testing AI tools, with names and identifying details removed.

To offer data, open an issue with the **Data offer** template. Describe what you have in general terms, roughly how much, and what consent covers it. **Do not attach or paste the data itself.** We will reply and arrange a private way to send it.

Data you send is used only to train and test this skill. It is kept out of every public repository, no participant's words are ever published, and it is deleted on request.

## Questions about the method

purpose-graphing is built using Indi Young's method, Data Science that Listens, and is not certified or endorsed by her. For the method itself, see [indiyoung.com](https://indiyoung.com).
