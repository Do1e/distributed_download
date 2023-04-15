import threading

class Thread(threading.Thread):
    def __init__(self, target, args):
        super().__init__()
        self.target = target
        self.args = args
        self.result = None

    def run(self):
        self.result = self.target(*self.args)

    def get_result(self):
        return self.result
