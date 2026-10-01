# Bugs

Read this before changing code. Each entry is a bug that was found and fixed, and what to do differently.

## Patterns
- Dropping non-ASCII characters loses information unless each character is converted first. Check every new character class against it (B1, B2, B4).
- A fallback value must differ for different inputs, or it causes collisions (B3).

## Bugs

### B4: Sharp s is dropped
- Found: 2026-10-01, while testing B1's fix with German titles
- Where: `slug.py`, `slugify`
- Symptom: `slugify("Straße")` returns `strae`. Expected `strasse`.
- Cause: `ß` has no NFKD split, so it is removed with the other non-ASCII characters. Checked.
- Fix: none yet. Waiting on open question 1 in the log.
- Test: `test_sharp_s_becomes_ss` (expected failure, strict)
- Lesson: NFKD only helps letters that have an accent to split off. Letters like `ß`, `ł` and `ø` need their own mapping.
- Status: Open

### B3: Every non-Latin title gets the same slug
- Found: 2026-10-01, introduced by approach 3.1 in the log
- Where: `slug.py`, `slugify`
- Symptom: `slugify("東京")` and `slugify("大阪")` both returned `post`.
- Cause: the fallback was a fixed word. Checked.
- Fix: fallback is `post-` plus the first 8 characters of a SHA-1 hash of the title.
- Test: `test_different_non_latin_titles_do_not_collide`
- Lesson: test a fallback with two different inputs, not one.
- Status: Fixed

### B2: Non-Latin titles give an empty slug
- Found: 2026-10-01, after the fix for B1
- Where: `slug.py`, `slugify`
- Symptom: `slugify("東京")` returned an empty string.
- Cause: Japanese characters have no ASCII form, so everything was dropped. Checked.
- Fix: the fallback from B3's fix.
- Test: `test_non_latin_title_is_not_empty`
- Lesson: after removing characters, check for an empty result.
- Status: Fixed

### B1: Accented letters are dropped
- Found: 2026-10-01, testing a French title
- Where: `slug.py`, `slugify`
- Symptom: `slugify("Café au lait")` returned `caf-au-lait`. Expected `cafe-au-lait`.
- Cause: `é` is outside a-z, so the regex treated it as punctuation. Checked.
- Fix: split accents off with Unicode NFKD, then drop non-ASCII.
- Test: `test_accents_are_kept_as_letters`
- Lesson: decide how non-ASCII input is handled before writing the regex.
- Status: Fixed
