
from serialview import SerialView
from unittest import TestCase, main


class CaseView(SerialView):
    _dump_key = _load_key = staticmethod(lambda x: str(x).lower())
    _dump_value = _load_value = staticmethod(lambda x: str(x).upper())


class TestMappingInterface(TestCase):
    
    def setUp(self):
        self.map = {}
        self.view = CaseView(self.map)
    
    def test_get(self):
        self.map.update(dict(
            a='lower',
            b='UPPER',
        ))
        self.assertEqual(self.view['a'], 'LOWER')
        self.assertEqual(self.view['A'], 'LOWER')
        self.assertEqual(self.view['b'], 'UPPER')
        self.assertEqual(self.view['B'], 'UPPER')
    
    def test_get_nokey(self):
        try:
            self.view['NotThere']
        except KeyError as e:
            self.assertEqual(e.args[0], 'NotThere')
        else:
            self.fail()
    
    def test_set(self):
        self.view['A'] = 'UPPER'
        self.view['b'] = 'lower'
        self.assertEqual(self.view['A'], 'UPPER')
        self.assertEqual(self.view['a'], 'UPPER')
        self.assertEqual(self.view['b'], 'LOWER')
    
    def test_in(self):
        self.view['key'] = 'value'
        self.assert_('key' in self.view)
        self.assert_('KEY' in self.view)
        self.assert_('no' not in self.view)
    
    def test_del(self):
        self.view['key'] = 'value'
        del self.view['KEY']
        self.assert_('key' not in self.view)
        



if __name__ == '__main__':
    main()