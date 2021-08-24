class InvalidOption(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass


class JobNotRunning(Exception):
    """
    Job Not Running
    """
    pass


class DuplicateName(Exception):
    """
    DuplicateName
    """
    pass
