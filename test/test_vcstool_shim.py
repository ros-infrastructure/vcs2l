import warnings

import vcs2l


def test_import_shim():
    with warnings.catch_warnings(record=True) as cap:
        warnings.simplefilter('always', DeprecationWarning)
        import vcstool  # noqa: PLC0415

    assert vcs2l.__version__ == vcstool.__version__

    w = next(iter(cap), None)
    assert issubclass(w.category, DeprecationWarning)
    assert "'vcstool' package is deprecated" in str(w.message)
