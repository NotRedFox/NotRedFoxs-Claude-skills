import hashlib
import re
import unicodedata


def slugify(title):
    text = unicodedata.normalize("NFKD", title)
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    if not slug:
        slug = "post-" + hashlib.sha1(title.encode("utf-8")).hexdigest()[:8]
    return slug
