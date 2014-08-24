# -----------------------------------------------------------------------------
class Error(Exception):
    def __init__(self, value):
        """
        input
        """
        self.value = value

    def __str__(self):
        """
        output
        """
        return repr(self.value)
