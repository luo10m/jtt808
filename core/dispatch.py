"""
According the message id,this function will dispatch each to
it destination!
"""
from utils.tools import is_subpackage
from utils.tools import is_encryption
from utils.tools import is_complete
from conf.protocols import MSG_ID
from conf.menu import REQ_RSP
from app.urls import urlpatterns
import tongue

"""
urlpatterns is a function Dicts,and it will automatic looking
for the target function according your menu_key is !
"""


def reflect(flag, request):
    urlpatterns[flag](request)


class Split:
    """
    This class expect a tuple,something like
    (126,1,0,1,2,1) and the class will split it
    to {'tag':126,'msg_id':(1,0),'msg_attr':(1,2)}
    """

    def __init__(self, val):

        self.message_head_content = val[1:-2]
        self.crc = val[-2]  # The crc encryption from terminal!
        self.debug = True
        if is_complete(self.message_head_content, self.crc):
            self.tag = val[0:1]
            self.msg_id = val[1:3]
            self.msg_attr = val[3:5]
            self.dev_id = val[5:11]
            self.msg_product = val[11:13]
            self.end_tag = val[-1:]
            # check if subpackage
            if is_subpackage(self.msg_attr):
                self.package_item = val[13:15]
                self.content = val[15:-2]
            else:
                # No message package item optional
                self.content = val[13:-2]
                # check if use CRC (Cyclic Redundancy Check)
                if is_encryption(self.msg_attr):
                    # TODO something for deciphering
                    pass
        else:
            # ignore this request from terminal device
            self.debug = False

    def show(self):
        if self.debug:
            print 'self.tag         :', self.tag
            print 'self.msg_id      :', self.msg_id
            print 'self.msg_attr    :', self.msg_attr
            print 'self.dev_id      :', self.dev_id
            print 'self.content     :', self.content
            print 'self.crc         :', self.crc
            print 'self.end_tag     :', self.end_tag
        else:
            print 'There are no assign because the crc have no right!'


class Dispatch:
    """
    According the JTT808 protocol, and what we should do
    depend on message id! so, if you want to know what current
    message id mean! you should ask the protocol!
    """

    def __init__(self, request, conn, menu=REQ_RSP, protocol=MSG_ID):
        self.protocol = protocol
        self.request = request
        self.conn = conn
        self.request_data = None
        self.rec_data = None
        self.msg_key = None
        self.menu = menu
        self.menu_key = None  # Just a key of urlpatterns Dicts
        self.resolution()
        self.middle = self.distribute()
        self.show()


    def resolution(self):
        self.request_data = tongue.Decode(self.request)
        self.rec_data = Split(self.request_data)
        self.menu_key = str(self.rec_data['msg_id'])

    def distribute(self):
        """

        :param : self.flag is a key of protocol Dicts!
        :param : self.conn is socket file desc
        :return:
        """

        # self.msg_key like '(1,2)' so, it's tuple-like

        if self.msg_key in self.protocol:
            self.menu_key = self.protocol[self.msg_key]
        # If you got the menu_key ,and you can check
        # which response will should call! so check the self.menu
        if self.menu_key in self.menu:
            return reflect(self.menu_key, self.rec_data)

        else:
            return None

    def show(self):
        print 'self.middle      :',self.middle

if __name__ == '__main__':
    # sample = (126, 1, 0, 0, 2, 78, 56, 45, 34, 25, 78, 0, 1, 51, 52, 43, 126)
    # result = Split(sample)
    # result.show()
    pass
