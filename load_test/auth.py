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
