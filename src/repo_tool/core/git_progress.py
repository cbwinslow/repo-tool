from git import RemoteProgress

class ProgressReporter(RemoteProgress):
    """GitPython progress reporter that forwards percentage to a callback."""

    def __init__(self, cb=None):
        super().__init__()
        self.cb = cb

    def update(self, op_code, cur_count, max_count=None, message=''):
        if max_count:
            percent = cur_count / float(max_count) * 100.0
            if self.cb:
                self.cb(percent, message)
