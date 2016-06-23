class GenAttrMapping:
    """
    Parses an <genAttrList> Element into a Mapping that supports duplicate keys
    """
    def __init__(self, data):
        self._items = tuple((elem.find('./name').text, elem.find('./value').text or '')
                            for elem in data.findall('./genAttrElem'))
        self._anyitem = dict(self._items)

    def __getitem__(self, name):
        return self._anyitem[name]

    def get(self, name, default=None):
        return self._anyitem.get(name, default)

    def __iter__(self, name):
        iter(n for n, v in self._items)

    def getall(self, name):
        return tuple(v for n, v in self._items if n == name)

    def items(self):
        yield from self._items
