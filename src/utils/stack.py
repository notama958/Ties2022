

class ColorStack():
    stack = []
    size = 0

    def __init__(self, *args, **kwargs):
        """"""

    def isEmpty(self):
        return len(self.stack) == 0

    def pop(self):
        """pop the last element"""
        if not self.isEmpty():
            self.stack.pop()
            self.size -= 1

    def peek(self):
        """peak the last element"""
        if not self.isEmpty():
            return self.stack[-1]
        return 0

    def push(self, value):
        """ push the value eg "RED",... """
        self.stack.append(value)
        self.size += 1
