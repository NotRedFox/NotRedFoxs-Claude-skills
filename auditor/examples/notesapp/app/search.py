class Search:
    def __init__(self, notes):
        self.notes = notes
        self.cache = {}

    def find(self, owner, query):
        key = (owner, query)
        if key not in self.cache:
            q = query.lower()
            self.cache[key] = [n for n in self.notes.list_for(owner) if q in n["text"].lower()]
        return self.cache[key]
