"""Build URL slugs from post titles."""

import hashlib
import re
import unicodedata


def slugify(title):
    """Return a lowercase, hyphen-separated slug for ``title``.

    Accented Latin letters keep their base letter (``Café`` becomes ``cafe``).
    Titles with no Latin letters at all get ``post-`` plus a short hash of the
    title, so different titles still get different slugs.
    """
    # NFKD splits a letter from its accent, so dropping non-ASCII afterwards
    # removes only the accent (B1).
    text = unicodedata.normalize("NFKD", title)
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    if not slug:
        # A fixed fallback word made every non-Latin title collide (B3).
        slug = "post-" + hashlib.sha1(title.encode("utf-8")).hexdigest()[:8]
    return slug
