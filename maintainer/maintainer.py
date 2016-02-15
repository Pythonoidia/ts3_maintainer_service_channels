import logging

import ts3

import configuration
from channels import ChannelsMaintanance

logging.basicConfig(level=logging.DEBUG)



def establish_connection():
    ts3conn = ts3.query.TS3Connection(configuration.ip, configuration.port)
    ts3conn.login(client_login_name=configuration.client_login_name, client_login_password=configuration.client_login_password)
    ts3conn.use(sid=configuration.sid)
    ts3conn.clientupdate(client_nickname="Huskar")
#    ts3conn.keepalive(10)
    return ts3conn




def main():
    ts3conn = establish_connection()
    x = ChannelsMaintanance(ts3conn, 7, 7)
    x.check_channels()

if __name__ == "__main__":
    main()


