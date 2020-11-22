import locust

from utils import client
import config


class LoadAuth(client.LoadClient):
    """Load testing of authentication system
    """

    @locust.task(1)
    def leave(self):
        """Log out, close session and finish
        """
        self.logout()
        self.interrupt()

    @locust.task(3)
    def stay(self):
        """Interrupt without closing session
        """
        self.interrupt()


class User(locust.HttpLocust):
    task_set = LoadAuth
    min_wait = 3000
    max_wait = 9000


load_plan = {
    'host': config.current_config.api_uri(),
    'num_requests': 10,
    'num_clients': 1,
    'hatch_rate': 1
}

if __name__ == '__main__':
    import sys
    import invokust

    locust_settings = invokust.create_settings(
        locustfile=sys.modules['__main__'].__file__, **load_plan)
    load_test = invokust.LocustLoadTest(locust_settings)
    load_test.run()
    load_test.stats()
