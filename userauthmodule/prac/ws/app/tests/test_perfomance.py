import time
from django.test import TestCase

class PerfomanceTest(TestCase):
    def test_query_perfomance(self):
        start = time.time()
        tasks = Task.objects.select_related('owner').all()
        list(tasks)
        duration = time.time() - start
        self.assertLess(duration,0.1)