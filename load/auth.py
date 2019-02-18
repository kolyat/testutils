import locust

from tools import gqlutils, rndutils
import settings


class Auth(locust.TaskSet, gqlutils.GqlClient):
    """Base class for load testing purposes
    """
    def on_start(self):
        """Log into system before start
        """
        user = 'user_{}'.format(rndutils.random_id())
        self.login(settings.LOGIN_PATH, username=user, password=user)

    @locust.task(1)
    def leave(self):
        """Log out, close session and finish
        """
        self.logout(settings.LOGOUT_PATH)
        self.cleanup()
        self.interrupt()

    @locust.task(3)
    def stay(self):
        """Interrupt without closing session
        """
        self.interrupt()


class User(locust.HttpLocust):
    task_set = Auth
    min_wait = 3000
    max_wait = 9000


load_plan = {
    'host': settings.BASE_URL,
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
