class Server:
    def __init__(self):
        super().__init__()

    def run(self):
        """
        implement this method to tell what the server should do
        """
        raise NotImplementedError("Method 'run' must be implemented to run the server!")

    def stop(self):
        """
        anything need to do to stop the server, e.x. finishing current job
        """
        pass
