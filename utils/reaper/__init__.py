import os
import logging


logging.basicConfig(
    filename=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '{}.log'.format(__name__)),
    filemode='a',
    format='%(asctime)s | [%(levelname)8s] | '
           '%(module)s.%(funcName)s(%(lineno)d) - %(message)s',
    level=logging.INFO
)
logging.getLogger(__name__).addHandler(logging.NullHandler())
