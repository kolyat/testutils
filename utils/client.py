from typing import Union
import re
import logging
import imapclient
import email
import keyring


log = logging.getLogger(__name__)


class EmailClient:
    """Client for e-mail processing.
    Now supports only IMAP4 protocol (over SSL).

    :ivar client: e-mail client instance
    :ivar current_folder: current selected folder in mailbox
    """

    def __init__(self, host: str, port: int = 993):
        """
        :param host: IMAP server
        :type host: str

        :param port: IMAP port (993 by default)
        :type port: int
        """
        self.client = imapclient.IMAPClient(host, port, ssl=True)
        self.current_folder = None

    def login(self, username: str):
        """Perform log-in to IMAP server.
        Password is retrieved automatically from local keyring storage.

        :param username: user's name / e-mail address
        :type username: str
        """
        self.client.login(username, keyring.get_password('system', username))

    def logout(self):
        """Perform log-out from IMAP server.
        """
        self.client.logout()

    def find_recovery_mail(self) -> Union[int, None]:
        """Search for latest password recovery mail.

        :return: mail's UID
        :rtype: int
        """
        inbox = 'INBOX'
        if self.current_folder != inbox:
            self.client.select_folder(inbox)
            self.current_folder = inbox
            log.info(f'Go to {inbox}')
        try:
            uid = max(self.client.search(['UNSEEN', 'TEXT', 'sendgrid']))
            log.info(f'Found latest recovery mail: UID #{uid}')
        except ValueError:
            uid = None
        return uid

    def get_recovery_link(self, uid: int) -> Union[str, None]:
        """Extract URL for password recovery from e-mail message.

        :param uid: mail's UID
        :type uid: int

        :return: password recovery URL
        :rtype: str
        """
        data = self.client.fetch(uid, 'RFC822')
        raw_msg = data[uid]
        decoded_msg = email.message_from_bytes(raw_msg[b'RFC822'])
        body = str(decoded_msg.get_payload(decode=True))
        try:
            r = re.search(r'href="(\S+sendgrid\S+)" target', body).group(1)
            log.info(f'Found password recovery link: {r}')
        except AttributeError:
            log.warning(f'Password recovery link was not found in #{uid}')
            r = None
        return r
