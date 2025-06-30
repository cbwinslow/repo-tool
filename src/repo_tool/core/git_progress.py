from git import RemoteProgress

class ProgressReporter(RemoteProgress):
    """GitPython progress reporter that forwards percentage to a callback."""

    def __init__(self, cb=None):
        """
        Initialize a ProgressReporter with an optional callback for progress updates.
        
        Parameters:
        	cb (callable, optional): A function to be called with progress percentage and message during updates.
        """
        super().__init__()
        self.cb = cb

    def update(self, op_code, cur_count, max_count=None, message=''):
        """
        Calculates progress percentage and invokes the callback with the current progress and message.
        
        If a maximum count is provided, computes the completion percentage based on the current count. If a callback is set, calls it with the calculated percentage and the provided message.
        """
        if max_count:
            percent = cur_count / float(max_count) * 100.0
            if self.cb:
                self.cb(percent, message)
