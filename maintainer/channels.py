import logging

from common import from_days_to_seconds, from_seconds_to_days


class ChannelsMaintanance(object):
    def __init__(self, ts3conn, quarantine_begin_time, quarantine_time):
        '''
        ts3conn - ts3.query.TS3Connection
        quarantine_begin_time - time in days after which the channels should be moved to quarantine
        quarantine_time - time in days before delatation of the channel which is inside quarantine
        '''
        self.conn = ts3conn
        self.qtime = from_days_to_seconds(quarantine_begin_time)
        self.deletation_time = from_days_to_seconds(quarantine_begin_time + quarantine_time)


    def check_channels(self):
        channels = self.conn.channellist()
        for channel in channels:
            self.check_channel(channel, channels)



    def check_channel(self, channel, channels):
            if channel['total_clients'] == '0':
                if not self.has_children(channel, channels):
                    if self.is_quarantine_time(channel):
                        if not self.in_quarantine(channel):
                            old_topic = self.conn.channelinfo(cid=channel['cid'])[0]['channel_topic']
                            logging.debug('Channel going to quarantine: '+ channel['channel_name'])
                            self.conn.channeledit(cid=channel['cid'], channel_topic='quarantine|'+old_topic)
                        else:
                            self.might_be_removed(channel)
                    #else:
                        #check if channel might be moved from quarantine to normal state

    def might_be_removed(self, channel):
        if not self.protected(channel):
            if self.is_deletation_time(channel):
                #self.comm.gm('Going to be removed: '+ channel['channel_name'])
                print('Going to be removed: '+ channel['channel_name'])
                self.conn.channeldelete(cid=channel['cid'], force=0)

    def protected(self, channel):
         if 'protected|' in self.conn.channelinfo(cid=channel['cid'])[0]['channel_topic']:
             logging.debug('Channel: '+channel['channel_name']+' is protected, so it will not be removed!')
             return 1

    def is_deletation_time(self, channel):
        info = self.conn.channelinfo(cid=channel['cid'])[0]
        if int(info['seconds_empty']) > self.deletation_time:
            logging.debug('Channel: '+ channel['channel_name']+ ' is going to be removed, as was not used for: '+ str(from_seconds_to_days(info['seconds_empty'])) + ' days')
            return 1


    def is_quarantine_time(self, channel):
        info = self.conn.channelinfo(cid=channel['cid'])[0]
        if int(info['seconds_empty']) > self.qtime or int(info['seconds_empty']) < 0:
            logging.debug('Channel: '+ channel['channel_name']+ ' was not used in past: '+ str(from_seconds_to_days(info['seconds_empty'])) + ' days')
            return 1

    def has_children(self, parent, channels):
        for channel in channels:
            if channel['pid'] == parent['cid']:
                logging.debug('Parent: '+parent['channel_name']+' has child: '+ str(channel['channel_name']))
                return 1
        else:
            return 0

    def in_quarantine(self, channel):
        if 'quarantine|' in self.conn.channelinfo(cid=channel['cid'])[0]['channel_topic']:
            logging.debug('already in quarantine')
            return 1

