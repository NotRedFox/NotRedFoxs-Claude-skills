# slugify

Turns blog post titles into short URL slugs, like `hello-world`.

```
python3 -m pytest
```

<!-- kick-start:architecture:start -->
## Architecture

Last updated 2026-10-01.

One function, `slugify`, turns a title into a slug. It has no dependencies outside the Python standard library. Tests live next to it.

| Path | What it does | Uses |
|---|---|---|
| `slug.py` | `slugify(title)`: builds the slug | `unicodedata`, `re`, `hashlib` |
| `test_slug.py` | Tests written from the goal, one per bug in `BUGS.md` | `pytest`, `slug.py` |
| `BUGS.md` | Bugs found and fixed, with lessons | |
| `kickstart/` | One log per working session | |

How a title becomes a slug:

1. Split accents off letters with Unicode NFKD.
2. Drop anything that is not ASCII, then lowercase.
3. Replace each run of characters outside a-z and 0-9 with one hyphen, and trim hyphens from the ends.
4. If nothing is left, use `post-` plus the first 8 characters of a SHA-1 hash of the title.
<!-- kick-start:architecture:end -->
