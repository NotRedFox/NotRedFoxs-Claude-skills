import re
from collections import Counter

WORD = re.compile(r"[a-z']+")


def count_words(text, ignore_case=True):
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    if ignore_case:
        text = text.lower()
    return Counter(WORD.findall(text))


def top_words(text, n=5, stopwords=None):
    counts = count_words(text)
    for w in stopwords or ():
        counts.pop(w, None)
    return counts.most_common(n)
