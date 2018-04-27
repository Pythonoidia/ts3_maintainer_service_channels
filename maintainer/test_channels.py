import unittest
from unittest.mock import Mock
from channels import ChannelsMaintanance


class TestChannelMaintenance(unittest.TestCase):
    def test_channels_to_quarantine(self):
        maintenance = ChannelsMaintanance(100)
        maintenance.channels_detailed_information = Mock(return_value={'2':[{"seconds_empty":101}]})
        maintenance._requests_post = Mock(return_value=None)
        result = maintenance.channels_to_quarantine()
        self.assertEqual(result, 'found channels that meet condition')

    def test_channels_to_quarantine_without_condition(self):
        maintenance = ChannelsMaintanance(100)
        maintenance.channels_detailed_information = Mock(return_value={'2':[{"seconds_empty":99}]})
        maintenance._requests_post = Mock(return_value=None)
        result = maintenance.channels_to_quarantine()
        self.assertEqual(result, None)

    def test_channels_to_quarantine_without_condition(self):
        maintenance = ChannelsMaintanance(100)
        maintenance.channels_detailed_information = Mock(return_value={'2':[{"channel_topic":"quarantine",
            "seconds_empty": 101}]})
        maintenance._requests_delete = Mock(return_value=None)
        result = maintenance.delete_parents()
        self.assertEqual(result, 'deleted channels 2') 

if __name__=='__main__':
    unittest.main()
