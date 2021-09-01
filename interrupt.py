from threading import Event


class BaseInterrupt(Event):

    def __init__(self, agent):
        super().__init__()
        self._agent = agent

    @property
    def agent(self):
        return self._agent

    @agent.setter
    def agent(self, val):
        raise PermissionError('cannot set Agent')

    # Deleter method
    @agent.deleter
    def agent(self):
        raise PermissionError('cannot delete agent')

    def interrupt_handler(self):
        """
        this function always run after Interrupt set by agent thread
        """
        print(24)


class StopInterrupt(BaseInterrupt):

    def interrupt_handler(self):
        print('StopInterrupt interrupt_handler was run')
        for job in self.agent.get_all_running_jobs():
            job.job_thread.join()


class NoneInterrupt(BaseInterrupt):
    """
    this Interrupt is for empty Interrupt
    and must only called in agent init phase
    """

    def __init__(self):
        Event.__init__(self)

    def interrupt_handler(self):
        pass
