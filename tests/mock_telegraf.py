"""
Minimum mock Telegraf for lolat unit testing purposes.
"""


class TelegrafClient():
    def __init__(self, host, port, tags):
        assert host == 'localhost'
        assert port == 8094
        assert tags == {'src': 'bucket'}

    def metric(self, measurement_name, values):
        assert measurement_name == 'lolat'
        assert values == {'reading': -1, 'volume': -1}
