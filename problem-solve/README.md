# Problem Solve

Version 1.0.0. See [CHANGELOG.md](CHANGELOG.md).

A Claude skill for problems where the normal route is closed: no API, no integration, "that can't be done". Instead of stopping, Claude climbs a ladder of approaches that get more creative at each step, and tests each one for real.

| Level | What it tries |
|---|---|
| 1. Obvious | Official API, SDK, existing library |
| 2. Sideways | Data exports, email or push notifications, feeds, the endpoints the site's own page uses, automating your own logged-in browser |
| 3. Different channel | Reading the effect instead of the system: sound, light, vibration, power draw, screen text, phone sensors |
| 4. Reframe | Solve an easier version, combine two weak signals, borrow an answer from another field |
| 5. Build it | A small device, script, extension or service that fills the gap |

How it works:

- **"Impossible" isn't an answer.** It treats "it's never been done" and "there's no API" as constraints to get around.
- **It asks what you have.** An old phone, a Raspberry Pi, a notification email, a browser that's always open. Your odd resources often turn out to be the answer, so they go on the ladder.
- **Nothing counts until it's tested.** Each approach gets the smallest test that proves or kills it, and the real result is logged. Tests that need your hardware are written out for you to run.
- **It writes a ChatGPT handoff.** You get a prompt to paste into ChatGPT with everything tried so far and what happened, so a different model can suggest new approaches without repeating old ones. Paste the answer back and Claude tests the promising ones. Research suggests ideas from one model narrow toward the same answers, and a second model widens them.
- **Creative, not reckless.** It won't break laws, get into accounts or systems you don't own, or get around security or paywalls. When it skips an approach for that reason, it logs why and keeps looking.
- **The handoff is scrubbed.** It goes to a third party, so personal details are replaced with placeholders.

## Example

[examples/washing-machine](examples/washing-machine/problem-solve/2026-10-01-washing-machine-done.md) is a real run on: "I want my phone to tell me when my washing machine finishes. It's an old machine, no wifi, no app, no API. I have an old Android phone and a Raspberry Pi in a drawer."

- It climbed all five levels and logged 12 approaches.
- The best answer is the old phone sitting on the washer, sending a push notification once a hard spin is followed by 6 minutes of stillness. It combines two weak signals because "no movement for a while" alone gave early alerts during soak pauses.
- The [test scripts](examples/washing-machine/problem-solve/tests/) re-run with the same results: 100 of 100 simulated cycles correct in each of two scenarios, against 30 to 34 early alerts for the simple version. The beep detector found every simulated beep at 0 dB (as loud as the room noise) and 16 of 20 at -5 dB, with no false alerts.
- These tests ran on simulated sensor data, because there was no washing machine to test on. The log says so next to every result and lists the real on-device test as the next step.
- [The ChatGPT handoff](examples/washing-machine/problem-solve/2026-10-01-washing-machine-done-chatgpt.md) lists all 10 approaches already tried, so ChatGPT starts from there.

## Install

### Claude app (claude.ai, desktop or phone)

1. Download [problem-solve.zip](https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/problem-solve.zip). Don't unzip it.
2. In Claude, open **Settings** and find **Skills**.
3. Upload the zip file.

### Claude Code

Paste this into your terminal (Mac or Linux):

```
mkdir -p ~/.claude/skills && curl -sL https://github.com/NotRedFox/NotRedFoxs-Claude-skills/raw/main/downloads/problem-solve.zip -o /tmp/problem-solve.zip && unzip -oq /tmp/problem-solve.zip -d ~/.claude/skills && rm /tmp/problem-solve.zip
```

Then restart Claude Code. On Windows, download the zip and unzip it into `.claude\skills` in your user folder.

To update later, do the same steps again.

## Use

- "Problem solve: <what you want to happen>"
- "There's no API for <thing>, find a way"
- "I'm stuck on <problem>"

The log goes in `problem-solve/<date>-<topic>.md` and the ChatGPT prompt in `problem-solve/<date>-<topic>-chatgpt.md`.

## Similar projects

- [obra/superpowers-skills, problem-solving set](https://github.com/obra/superpowers-skills/blob/main/skills/problem-solving/ABOUT.md): thinking techniques such as inversion and collision-zone thinking for when you're stuck. Problem Solve adds the ladder, real tests at each step and the second-model handoff.
- Second-opinion plugins such as [consult](https://github.com/agent-sh/consult) and [the-council](https://github.com/DantesPeak85/the-council) send a question from Claude to another model by API. Problem Solve uses a prompt you paste, so it works without API keys.

## Research

- Si, Yang and Hashimoto, [Can LLMs Generate Novel Research Ideas?](https://arxiv.org/abs/2409.04109) (2024): model ideas were rated more novel than experts' but less feasible, and varied little. Hence real tests and a second model.
- Doshi and Hauser, [Generative AI enhances individual creativity but reduces the collective diversity of novel content](https://www.science.org/doi/10.1126/sciadv.adn5290) (Science Advances, 2024)
- Gick and Holyoak, [Analogical problem solving](https://deepblue.lib.umich.edu/handle/2027.42/23210) (Cognitive Psychology, 1980): solutions can come from distant analogies
- [AutoTRIZ](https://arxiv.org/abs/2403.13002): TRIZ, a systematic method for removing contradictions, applied with language models
