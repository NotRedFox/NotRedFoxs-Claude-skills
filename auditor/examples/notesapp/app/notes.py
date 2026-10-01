import time


class Notes:
    def __init__(self):
        self.notes = {}
        self.next_id = 1

    def create(self, owner, text, tags=None):
        tags = list(tags or [])
        nid = self.next_id
        time.sleep(0.001)
        self.next_id = nid + 1
        tags.append("note")
        note = {"id": nid, "owner": owner, "text": text, "tags": tags}
        self.notes[nid] = note
        return note

    def list_for(self, owner):
        return [n for n in self.notes.values() if n["owner"] == owner]
