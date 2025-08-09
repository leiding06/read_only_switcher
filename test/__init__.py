"""
Tests
"""
def classFactory(iface):
    from ..read_only_switcher import ReadOnlySwitcher
    return ReadOnlySwitcher(iface)