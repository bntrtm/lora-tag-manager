from tkinter import Entry, END

class Queue:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.insert(0, item)

    def pop(self):
        if len(self.items) == 0:
            return None
        item = self.items[len(self.items)-1]
        del self.items[-1]
        return item

    def peek(self):
        if len(self.items) == 0:
            return None
        return self.items[-1]

    def size(self):
        return len(self.items)


class Trie:
    def __init__(self):
        self.root = {}
        self.end_symbol = "*"
    
    def longest_common_prefix(self):
        current = self.root
        prefix = ''
        while True:
            keys = list(current.keys())
            if self.end_symbol in keys:
                break
            if len(keys) == 1:
                prefix = prefix + keys[0]
                current = current[keys[0]]
            else:
                break
        return prefix

    def find_matches(self, document):
        matches = set()
        for i in range(len(document)):
            current = self.root
            for j in range(i, len(document)):
                if document[j] not in current:
                    break
                current = current[document[j]]
                if self.end_symbol in current:
                    matches.add(document[i:j+1])
        return matches

    def search_level(self, current_level, current_prefix, words):
        if self.end_symbol in current_level:
            words.append(current_prefix)
        for key in sorted(current_level):
            if key != self.end_symbol:
                self.search_level(current_level[key], (current_prefix + key), words)
        return words
    
    def words_with_prefix(self, prefix):
        matching = []
        current = self.root
        for c in prefix:
            if c not in current:
                return []
            current = current[c]
        self.search_level(current, prefix, matching)
        return matching

    def exists(self, word):
        current = self.root
        for char in word:
            if char in current:
                current = current[char]
            else:
                return False
        if self.end_symbol in current:
            return True
        return False
    
    def add(self, word):
        current = self.root
        for char in word:
            if char not in current:
                current[char] = {}
            current = current[char]
        current[self.end_symbol] = True
    
