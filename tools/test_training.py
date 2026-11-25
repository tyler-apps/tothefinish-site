import unittest
from check_home_numbers import normalize

class NumbersOnlyHomepageTests(unittest.TestCase):
    def test_generated_values_can_change(self):
        self.assertEqual(normalize('<span data-k="wkdone">4.0</span>'),normalize('<span data-k="wkdone">9.2</span>'))
    def test_prose_and_navigation_cannot_change(self):
        for a,b in [('<p>A story</p>','<p>A different story</p>'),('<a href="/training/">Training</a>','<a href="/other/">Training</a>')]:
            self.assertNotEqual(normalize(a),normalize(b))
    def test_unrecognized_hook_is_not_ignored(self):
        self.assertNotEqual(normalize('<span data-k="anything">A</span>'),normalize('<span data-k="anything">B</span>'))
if __name__=='__main__': unittest.main()
