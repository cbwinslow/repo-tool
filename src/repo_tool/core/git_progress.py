from git import RemoteProgress

class ProgressReporter(RemoteProgress):
    """GitPython progress reporter that forwards percentage to a callback."""

    def __init__(self, cb=None):
        """
        Initialize the ProgressReporter with an optional callback function.
        
        Parameters:
        	cb (callable, optional): A function to be called with progress updates. Should accept two arguments: percentage (float) and message (str).
        """
        super().__init__()
        self.cb = cb

    def update(self, op_code, cur_count, max_count=None, message=''):
        """
        Handles progress updates by calculating the completion percentage and invoking the callback with the percentage and message.
        
        Parameters:
            op_code: Operation code indicating the type of Git operation.
            cur_count: The current progress count.
            max_count: The maximum count for the operation, used to compute percentage.
            message: Optional message describing the current progress state.
        """
        if max_count:
            percent = cur_count / float(max_count) * 100.0
            if self.cb:
                self.cb(percent, message)
