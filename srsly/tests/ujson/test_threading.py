import threading

from srsly import ujson


def _hammer(target, mutate, n_encoders=4, n_iter=2000):
    """Encode `target` from several threads while another thread mutates it.
    On a free-threaded build, an encoder that holds borrowed references into
    `target` reads freed memory and crashes the interpreter."""
    stop = threading.Event()
    errors = []

    def mutator():
        while not stop.is_set():
            mutate(target)

    def encoder(sort_keys):
        try:
            for _ in range(n_iter):
                try:
                    ujson.dumps(target, sort_keys=sort_keys)
                except (RuntimeError, KeyError):
                    # "dictionary changed size during iteration", or a key
                    # removed between iterating and looking it up, is fine.
                    pass
        except Exception as e:  # pragma: no cover
            errors.append(e)

    threads = [threading.Thread(target=mutator)]
    threads += [
        threading.Thread(target=encoder, args=(i % 2 == 0,))
        for i in range(n_encoders)
    ]
    for t in threads[1:]:
        t.start()
    threads[0].start()
    for t in threads[1:]:
        t.join()
    stop.set()
    threads[0].join()
    assert not errors


def test_encode_list_while_mutating():
    def mutate(items):
        # Slice assignment frees the previous items immediately.
        items[:] = [["x" * 100, {"a": [1.5]}] for _ in range(200)]
        items[:] = [{"b": "y" * 100}]

    _hammer([], mutate)


def test_encode_dict_while_mutating():
    def mutate(d):
        for i in range(200):
            d[str(i)] = ["x" * 100, {"k": i}]
        for i in range(200):
            d[str(i)] = "y" * 100
        d.clear()

    _hammer({}, mutate)


def test_encode_list_shrunk_by_callback():
    items = []

    class Shrinker:
        def __json__(self):
            del items[:]
            return '"shrunk"'

    items.extend([Shrinker()] + [{"a": "x" * 100}] * 20)
    assert ujson.dumps(items).startswith('["shrunk"')
