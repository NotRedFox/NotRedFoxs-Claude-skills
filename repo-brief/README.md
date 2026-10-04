# Repo Brief

Two small Python scripts (no installs needed) for checking on a project from your phone, or asking about it, without spending Claude tokens and without sending your code anywhere.

- **`brief.py`** writes `BRIEF.md`: a map of your repo with no code bodies. For each file it lists what it's for and the names of its functions, plus recent commits, files changed lately, uncommitted work and TODOs. On this repo that's about 6,000 tokens.
- **`ask.py`** sends `BRIEF.md` and your question to Gemini's free API and prints the answer. It sends nothing else.

## What it's good for, and what it isn't

Good for: "what changed this week?", "where is the login code?", "what's left on the TODO list?", "explain how this project fits together".

Not good for: finding bugs or checking whether code is correct. The brief has no code bodies, so Gemini can only say which file to look at. That is the price of keeping your code out of it.

It also works with Claude: pasting `BRIEF.md` into a Claude chat costs about 6,000 tokens, much less than letting Claude read the whole repo.

## Privacy

On Gemini's free tier, Google may use what you send to improve its products, and human reviewers may read it. The paid tier doesn't do this. So the brief leaves out:

- all code bodies
- files like `.env`, `*.pem`, `*.key` and `credentials*`
- anything that looks like an API key or token, and email addresses, which are replaced with `[secret]` and `[email]`

It still includes file names, function names, comments at the top of files, commit messages and TODO text. Run `python3 ask.py "test" --dry-run` to see how much would be sent, and read `BRIEF.md` before you send it the first time. If a project is private for a reason, don't send it to a free tier.

## Use it

Copy `brief.py` and `ask.py` into your project, then:

```
python3 brief.py
python3 ask.py "what changed this week?"
```

`ask.py` needs a free key from [Google AI Studio](https://aistudio.google.com/apikey). Set it with `export GEMINI_API_KEY=your-key`. It uses `gemini-flash-latest` unless you set `GEMINI_MODEL`.

## Keep it updated for your phone

To keep `BRIEF.md` current on GitHub after every push:

1. Copy `brief.py` to `.github/brief.py` in your project.
2. Copy `brief.yml` to `.github/workflows/brief.yml`.

On your phone, open `BRIEF.md` on GitHub to read it, or attach it in the Gemini or Claude app and ask about it. The Gemini app has its own data rules, separate from the API's.

## Tested

- `brief.py` on this repo: 24,000 characters, no code bodies.
- On a test repo with a `.env` file, a `.pem` file, an API key and a token in comments, and emails in a comment and a commit message: none of them reached `BRIEF.md`.
- `ask.py` against a local stand-in for Gemini's API: correct address, key sent in a header rather than the URL, only the brief and the question sent, and the answer and token counts printed.
- Against Google's real server with a fake key, it shows Google's "API key not valid" error. I couldn't test a real answer without a key.
- The workflow's commands, run locally on a fresh clone. The workflow itself hasn't run on GitHub yet.
