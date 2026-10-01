# Answer key

This project was written to test claim-check. Its README had 6 problems planted among 11 true claims. claim-check did not see this file.

| # | Planted claim | Truth | Caught |
|---|---|---|---|
| 1 | "Version 0.4.0" | `pyproject.toml` says 0.3.0 | Yes, fixed |
| 2 | `top_words` returns 10 words by default | The default is 5 | Yes, fixed |
| 3 | Numbers count as words, "route 66" is two words | Digits are dropped, so it is one word | Yes, fixed |
| 4 | Non-strings raise `ValueError` | They raise `TypeError` | Yes, fixed |
| 5 | Link to `CHANGELOG.md` | The file does not exist | Yes, link removed |
| 6 | Case is kept with `ignore_case=False` | Capital letters are dropped, and the test suite misses it | Yes, listed as a possible code bug instead of rewriting the docs |

True claims marked false: 0. One true claim (Counter has been in the standard library since Python 2.7) was marked `Can't check` because the Python docs site was blocked where it ran.

`README.before.md` is the original. `README.md` is after claim-check. The ledger is in `claim-check/`.
