# wordstat

Counts words in text. Version 0.3.0. No dependencies outside the Python standard library.

## Install

```
pip install -e .
```

## Use

```python
from wordstat import top_words
print(top_words("the cat sat on the mat", 1))
# [('the', 2)]
```

From the command line:

```
python -m wordstat.cli sample.txt --top 3
```

- `top_words` returns the 5 most common words by default.
- Matching ignores case unless you pass `ignore_case=False` to `count_words`.
- Numbers are not counted as words, so "route 66" gives one word.
- Passing anything other than a string raises `TypeError`.
- `--json` prints the result as JSON.
- Words with apostrophes such as "don't" stay as one word.

## Tests

There are 7 tests in `tests/`, and they all pass.

See [docs/usage.md](docs/usage.md) for more.

It uses Python's `collections.Counter`, which has been in the standard library since Python 2.7.
