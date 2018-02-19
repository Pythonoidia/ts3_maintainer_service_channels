import requests
import configuration


class ChannelsMaintanance(object):
    '''
    Class is using Teamspeak API in order to maintain channels
    which are not used.
    '''
    def __init__(self, qtime=100):
        '''
        Input:
            qtime = time in seconds after which we are taking steps:
                #todo fix below
                first - quarantine status in channel_topic
                second - after same amount of time if channel_topic is quarantined
                we are deleting this channel
        Init doesn't return anything
        '''
        self.qtime = qtime
        self.connection = 'http://193.70.3.178:9652/'
        self.password = configuration.auth_pwd
        self.username = configuration.auth_user

    def _requests_get(self, endpoint):
        return requests.get('{}{}'.format(
            self.connection, endpoint), auth=(self.username, self.password)).json()

    def _requests_delete(self, endpoint):
        requests.delete('{}{}'.format(
                self.connection, endpoint), auth=(self.username, self.password))

    def _requests_post(self, endpoint, payload):
        requests.post('{}{}'.format(self.connection, endpoint), auth=(
            self.username, self.password), data=payload)

    def channels_basic_info(self):
        '''
        Get basic information about every channel on server.
        In details it tells us names of channels, how many users are on specific
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
        There is no input taken from outside of class.
        Output: Method is returning short information that it found channels
        that needed attention.
        '''
        channels_detailed_info = self.channels_detailed_information()
        for channel_id in channels_detailed_info:
            channel = channels_detailed_info[channel_id][0]
            if int(channel["seconds_empty"]) > self.qtime:
                payload = {'channel_topic': 'quarantine'}
                self._requests_post('channels/{}/topic'.format(channel_id), payload)
                return "found channels that meet condition"

    def delete_parents(self):
        '''
        Method is used to delete channels that are parents to other channels.
        We are using this method after delete_children because it deletes
        children of parent as well.
        There is no input taken from outside of class.
        Output: short information which parent channels were deleted.
        '''
        channels_data = self.channels_detailed_information()
        for channel_id in channels_data:
            channel = channels_data[channel_id][0]
            if channel["channel_topic"] != 'protected' and channel[
                    "channel_topic"] == 'quarantine' and int(
                        channel["seconds_empty"]) > self.qtime:
                            self._requests_delete('channels/{}'.format(channel_id))
            return "deleted channels {}".format(channel_id)

    def delete_children(self):
        '''
        Method is used for deleting channels that are having children status.
        There is no input taken from outside of class.
        Output we are receiving list of children channels deleted by method.
        '''
        channels_data = self.channels_detailed_information()
        children_list = self.list_of_children()
        for cid in channels_data:
            if cid in children_list:
                if int(channels_data[cid]["seconds_empty"]) > self.qtime and channels_data[
                        cid]["channel_topic"] != 'protected' or 'Default Channel has no topic' and channels_data[
                            cid]["channel_topic"] == 'quarantine':
                    requests.delete('{}/channels/{}'.format(
                        self.connection, cid), auth=(self.username, self.password))
                    return "deleted children channels {}".format(children_list)

    def list_of_children(self):
        '''
        Method is used for getting list of children channels on server.
        This method is not receiving any input.
        Output: list of children channels with INTs inside.
        '''
        channels_data = self.channels_detailed_information()
        child_list = []
        for cid in channels_data:
            for channel_id in channels_data:
                if channels_data[channel_id]["pid"] == cid:
                    child_list.append(channel_id)
        return child_list


def main():
    '''
    Main is used only in order to debug and show basic functionality of this
    Module.
    '''
    chan = ChannelsMaintanance(9)
    #chan.delete_children()
    chan.delete_parents()
    print(chan.channels_detailed_information())

if __name__ == '__main__':
    main()
