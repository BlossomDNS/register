from threading import Thread

'''
concurrency.py

Code here is designed to speed up certain processes that might take too long

ThreadWithReturnValue is used on functions that returns a certain variable
'''
class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

def cloudf_doms(CLOUDFLARE_DOMAINS, CLOUDFLARE) -> list:
    all_sub_domains = []
    for all_domain in CLOUDFLARE_DOMAINS:
        records = CLOUDFLARE[all_domain["url"]].getDNSrecords()
        for record in records:
            all_sub_domains.append(record)
    return all_sub_domains