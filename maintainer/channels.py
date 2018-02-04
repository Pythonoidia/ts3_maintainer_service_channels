import logging
import configuration
import requests
from common import from_days_to_seconds, from_seconds_to_days


class ChannelsMaintanance(object):
    def __init__(self, quarantine_begin_time, quarantine_time):
        '''
        ts3conn - ts3.query.TS3Connection
        quarantine_begin_time - time in days after which the channels should be moved to quarantine
        quarantine_time - time in days before delatation of the channel which is inside quarantine
        '''
        self.qtime = from_seconds_to_days(quarantine_begin_time)
        self.deletation_time = from_days_to_seconds(quarantine_begin_time + quarantine_time)
        self.connection = 'http://193.70.3.178:9652/'
        self.password = configuration.auth_pwd
        self.username = configuration.auth_user

    def channels_list(self):
        channels = requests.get('{}channels'.format(self.connection), auth=(self.username, self.password)).json()
        channels_list = []
        for channel in channels:
            channels_list.append(channel)
        return channels_list

    def channel_detailed_information(self):
        channels_list = self.channels_list()
        channels_info = {}
        for channel in channels_list:
            channels_info[channel["cid"]] = requests.get('{}channels/{}'.format(self.connection, channel["cid"]), auth=(self.username, self.password)).json()
        return channels_info

    def channels_to_quarantine(self):
        channels_info = self.channel_detailed_information()
        for channels in channels_info:
            for channel in channels_info[channels]:
                if int(channel["seconds_empty"]) > self.qtime:
                    payload = {'channel_topic':'quarantine'}
                    print(channels, channel["seconds_empty"])
                    requests.post('{}channels/{}/topic'.format(self.connection, channels), auth=(self.username, self.password), data = payload)
        return 1

    def might_be_removed(self):
        '''
        My problem at this moment is that commented lines are deleting
        parent and children if they are innactive, instead of deleting
        only children.
        '''
        channels_data = self.channel_detailed_information()
        for channels in channels_data:
            for channel in channels_data[channels]:
                print(channel)
                #if channel["channel_topic"] != 'protected' and int(channel["seconds_empty"]) > self.qtime:
                    #requests.delete('{}/channels/{}'.format(self.connection, channels), auth=(self.username, self.password))
        '''self.conn.channeldelete(cid=channel['cid'], force=0)'''

    def has_children(self, parent, channels):
        for channel in channels:
            if channel['pid'] == parent['cid']:
                logging.debug('Parent: '+parent['channel_name']+' has child: '+ str(channel['channel_name']))
                return 1
        else:
            return 0

def main():
    chan = ChannelsMaintanance(0.01, 10)
    #print(chan.channel_detailed_information())
    #print(chan.channels_to_quarantine())
    print(chan.might_be_removed())

if __name__ == '__main__':
    main()
