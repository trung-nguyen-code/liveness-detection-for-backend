from collections.abc import Mapping


def extract_key_from_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    return None


class safe_itemgetter:
    """
    Return a callable object that fetches the given item(s)
    from its operand.
    """

    __slots__ = ("_items", "_call")

    def __init__(self, item, *items, default=None):
        if not items:
            self._items = (item,)

            def func(obj):
                if isinstance(obj, Mapping):
                    return obj.get(item, default)
                if (item > 0 and len(obj) <= item) or (
                    item < 0 and len(obj) < abs(item)
                ):
                    return default
                return obj[item]

            self._call = func
        else:
            self._items = items = (item,) + items

            def func(obj):
                if isinstance(obj, Mapping):
                    get = obj.get  # Reduce attibute search call.
                    return tuple(get(i, default) for i in items)

                return tuple(
                    default
                    if (i > 0 and len(obj) <= i) or (i < 0 and len(obj) < abs(i))
                    else obj[i]
                    for i in items
                )

            self._call = func

    # ----------------- same as operator.itemgetter --------------#

    def __call__(self, obj):
        return self._call(obj)

    def __repr__(self):
        return "%s.%s(%s)" % (
            self.__class__.__module__,
            self.__class__.__name__,
            ", ".join(map(repr, self._items)),
        )

    def __reduce__(self):
        return self.__class__, self._items
