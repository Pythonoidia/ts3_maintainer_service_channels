import logging
import requests
import configuration
from common import from_days_to_seconds


class ChannelsMaintanance(object):
    def __init__(self, qtime=2):
        '''
        Input:
            qtime = time in days after which we are taking steps:
                first - we are changing topic of channel to "quarantine" in order to
                mark it as qualified to deleting it in future
                second - after same amount of time if channel_topic is quarantined
                we are deleting this channel
        '''
        self.qtime = from_days_to_seconds(qtime)
        self.url = configuration.url
        self.password = configuration.auth_pwd
        self.username = configuration.auth_user

    def _requests_get(self, endpoint):
        return requests.get('{}{}'.format(
            self.url, endpoint), auth=(self.username, self.password)).json()

    def _requests_delete(self, endpoint):
        requests.delete('{}{}'.format(
            self.url, endpoint), auth=(self.username, self.password))

    def _requests_post(self, endpoint, payload):
        requests.post('{}{}'.format(self.url, endpoint), auth=(
            self.username, self.password), data=payload)

    def channels_basic_info(self):
        '''
        Get basic information about every channel on server.
        In details it tells us names of channels, how many users are on different
        channels, and channel_id with parent_id.
        Output: channels_basic_info as list of dictionaries.
        '''
        channels = self._requests_get('channels')
        channels_basic_info = []
        for channel in channels:
            channels_basic_info.append(channel)
        return channels_basic_info

    def channels_detailed_information(self):
        '''
        Method is returning more data than channels_basic_info method.
        In this method we are receiving important data such as: channel_topic
        or seconds_empty that allow us to see if there is any status written
        into topic or if channel is used at all.
        There is no input value from outside of class.
        Output: channels_detailed_info as dictionary of dictionaries in form of:
            cid: detailed_info of one channel
        '''
        channels_basic_info = self.channels_basic_info()
        channels_detailed_info = {}
        for channel in channels_basic_info:
            channels_detailed_info[channel["cid"]] = self._requests_get(
                'channels/{}'.format(channel["cid"]))
        return channels_detailed_info

    def channels_to_quarantine(self):
        '''
        Method is using channels_detailed_information for getting seconds_empty
        and channel_topic values in order to specify if there should be put
        status of quarantine on channels that meet certain condition.
        '''
        channels_detailed_info = self.channels_detailed_information()
        for channel_id in channels_detailed_info:
            channel = channels_detailed_info[channel_id]
            if int(channel["seconds_empty"]) > self.qtime and channel[
                    "channel_topic"] != 'protected':
                payload = {'channel_topic': 'quarantine'}
                self._requests_post('channels/{}/topic'.format(channel_id), payload)
                logging.debug("quarantined channel: {}".format(channel_id))

    def delete_parents(self):
        '''
        Method is used to delete channels that are parents to other channels.
        We are using this method after delete_children because it deletes
        children of parent as well.
        '''
        channels_data = self.channels_detailed_information()
        for channel_id in channels_data:
            channel = channels_data[channel_id]
            if not 'protected' in channel["channel_topic"] and 'quarantine' in channel["channel_topic"] and int(channel["seconds_empty"]) > self.qtime:
                self._requests_delete('channels/{}'.format(channel_id))
            logging.debug("deleted channel {}".format(channel_id))

    def delete_children(self):
        '''
        Method is used for deleting channels that are having children status.
        '''
        channels_data = self.channels_detailed_information()
        children_list = self.list_of_children()
        for cid in channels_data:
            if cid in children_list:
                if not 'protected' in channels_data[cid]["channel_topic"] and 'quarantine' in channels_data[cid]["channel_topic"] and int(channels_data[cid]["seconds_empty"]) > self.qtime:
                    requests.delete('{}/channels/{}'.format(
                        self.url, cid), auth=(self.username, self.password))
                    logging.debug("deleted children channel {}".format(cid))

    def list_of_children(self):
        '''
        Method is used for getting list of children channels on server.
        '''
        channels_data = self.channels_detailed_information()
        child_list = []
        for cid in channels_data:
            for channel_id in channels_data:
                if channels_data[channel_id]["pid"] == cid:
                    child_list.append(channel_id)
        return child_list

def main():
    channels = ChannelsMaintanance()
    channels.delete_parents()
    channels.delete_children()

if __name__ == "__main__":
    main()

