from .delegator import Delegator
from .redirector import WidgetRedirector


class Percolator:

    def __init__(self, text):
        # XXX would be nice to inherit from Delegator
        self.text = text
        self.redir = WidgetRedirector(text)
        self.top = self.bottom = Delegator(text)
        self.bottom.insert = self.redir.register("insert", self.insert)
        self.bottom.delete = self.redir.register("delete", self.delete)
        self.filters = []

    def close(self):
        while self.top is not self.bottom:
            self.removefilter(self.top)
        self.top = None
        self.bottom.setdelegate(None)
        self.bottom = None
        self.redir.close()
        self.redir = None
        self.text = None

    def insert(self, index, chars, tags=None):
        # Could go away if inheriting from Delegator
        self.top.insert(index, chars)
        self.top.update()
        self.top.focus_set()
        self.top.tag_add("TODO", "0.0", "end")
        self.top.recolorize_main()

    def delete(self, index1, index2=None):
        # Could go away if inheriting from Delegator
        self.top.delete(index1, index2)
        self.top.update()
        self.top.focus_set()
        self.top.tag_add("TODO", "0.0", "end")
        self.top.recolorize_main()

    def insertfilter(self, filter):
        # Perhaps rename to pushfilter()?
        assert isinstance(filter, Delegator)
        assert filter.delegate is None
        filter.setdelegate(self.top)
        self.top = filter

    def removefilter(self, filter):
        # XXX Perhaps should only support popfilter()?
        assert isinstance(filter, Delegator)
        assert filter.delegate is not None
        f = self.top
        if f is filter:
            self.top = filter.delegate
            filter.setdelegate(None)
        else:
            while f.delegate is not filter:
                assert f is not self.bottom
                f.resetcache()
                f = f.delegate
            f.setdelegate(filter.delegate)
            filter.setdelegate(None)