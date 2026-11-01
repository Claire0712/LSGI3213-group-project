import unittest
from analyze import parse_events
class EventAccountingTest(unittest.TestCase):
    def test_completed_stuck_same_link_and_full_traversals(self):
        e=[dict(time='0',type='departure',person='a',legMode='car'),dict(time='1',type='entered link',vehicle='a',link='11'),dict(time='11',type='left link',vehicle='a',link='11'),dict(time='12',type='arrival',person='a',legMode='car'),dict(time='20',type='departure',person='a',legMode='car'),dict(time='20',type='arrival',person='a',legMode='car'),dict(time='30',type='departure',person='b',legMode='car'),dict(time='40',type='stuckAndAbort',person='b',legMode='car')]
        r=parse_events(e)
        self.assertEqual([t['travel_s'] for t in r['trips']],[12,0])
        self.assertEqual(r['stuck'],1)
        self.assertEqual(r['unmatched_departures'],0)
        self.assertEqual(r['traversals'][0]['travel_s'],10)
        self.assertEqual(r['departures'],3)
if __name__=='__main__':unittest.main()
