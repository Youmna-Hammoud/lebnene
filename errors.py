class LebneneError(SyntaxError):
    def __init__(self, message, line=None):
        self.line = line
        if line is not None:
            message = f"[satr {line}] {message}"
        super().__init__(message)
