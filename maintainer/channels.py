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
        self.qtime = 100
        #self.qtime = from_seconds_to_days(quarantine_begin_time)
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

    def channels_detailed_information(self):
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

    def might_be_removed_parent(self):
        channels_data = self.channel_detailed_information()
        for channels in channels_data:
            for channel in channels_data[channels]:
                if channel["channel_topic"] != 'protected' and int(channel["seconds_empty"]) > self.qtime:
                    print("in the loop")
                    requests.delete('{}/channels/{}'.format(self.connection, channels), auth=(self.username, self.password))

    def might_be_removed_children(self):
        channels_data = self.channels_detailed_information()
        for cid in channels_data:
            for channel_id in channels_data:
                if channels_data[channel_id]['pid'] == cid:
                    '''
                    Czemu wykorzystany jest cid z pierwszego fora skoro mozna sciagnac channel_id
                    z drugiego, de facto mozna pozbyc sie jednego fora?
                    Czy ta struktura jest zrobiona wlasnie na potrzeby kompletnego sprawdzenia danych?
                    Mam tu na mysli majac pelen komplet cid po zakonczeniu pracy jednej petli sprawdzamy
                    na biezaco pid w drugiej petli?
                    '''
                    print('To jest id dziecka:', channel_id, 'dla kanalu: ', cid)
            #print('cid:', cid, 'pid:', channel_data['pid'], channel_data["channel_name"])
            #if 'protected' in channel_data["channel_topic"] and int(channel_data["seconds_empty"]) > self.qtime and cid == channel_data["pid"]:
            #    print("found match")
                   #requests.delete('{}/channels/{}'.format(self.connection, channels), auth=(self.username, self.password))
                    #return 'done'

    def another_removed(self):
        #to podejscie daje mi jedynie CID kanalow ktore na pewno sa rodzicami
        #jest to bledne podejscie ale mozna z tego zrobic metode ktora zwraca liste
        #rodzicow ktorzy istnieja na serwerze
        '''
        channels_data = self.channels_detailed_information()
        cid_list = []
        pid_list = []
        for cid in channels_data:
            cid_list.append(cid)
            pid_list.append(channels_data[cid]["pid"])
        print(cid_list, pid_list)
        return set(pid_list).intersection(cid_list)
        '''

        #tak powinna wygladac funkcja zwracajaca liste dzieci
        #nie do tego daze ale mozna to wykorzystac jako osobny modul
        channels_data = self.channels_detailed_information()
        child_list = []
        for cid in channels_data:
            for channel_id in channels_data:
                if channels_data[channel_id]["pid"] == cid:
                    child_list.append(channel_id)
        print(child_list)


    def has_children(self, parent, channels):
        for channel in channels:
            if channel['pid'] == parent['cid']:
                logging.debug('Parent: '+parent['channel_name']+' has child: '+ str(channel['channel_name']))
                return 1
        else:
            return 0

def main():
    chan = ChannelsMaintanance(9, 10)
    #print(chan.channel_detailed_information())
    #print(chan.channels_to_quarantine())
    print(chan.might_be_removed_children())
    print(chan.another_removed())
    #chan.might_be_removed_parent()
if __name__ == '__main__':
    main()


'''

1. check if channel topic is default
2. check if channel topic has "protected" in it.
3. check if channel did not have any user for 7 days. (and add quarantine to topic)
4. check if channel has childs. it means that we have to check every channel if it has this channel as a parent.

'''

