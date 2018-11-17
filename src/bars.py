import mido


def extract_bars(ticks_per_beat, messages):
    messages_with_meta = inject_bar_meta(ticks_per_beat, messages)

    bars = []
    for message in messages_with_meta:
        if 'time_signature' == message.type:
            bars.append(Bar([]))
        bars[-1].messages.append(message)

    return bars


def inject_bar_meta(ticks_per_beat, messages):
    output_messages = []
    time_signature = None
    bar_tick = 0
    for message in messages:
        if message.type == 'time_signature':
            time_signature = TimeSignature(ticks_per_beat, message.numerator, message.denominator)
            output_messages.append(message)
            bar_tick = 0
        elif time_signature:
            if time_signature.within_bar(bar_tick + message.time):
                output_messages.append(message)
                bar_tick += message.time
            else:
                output_messages.append(mido.MetaMessage(
                    'time_signature', time=time_signature.next_bar_start_delta(bar_tick),
                    numerator=4, denominator=4))
                output_messages.append(
                    message.copy(time=message.time - time_signature.next_bar_start_delta(bar_tick)))
                bar_tick = 0

    return output_messages


def bar_ticks(ticks_per_beat, numerator, denominator):
    return ticks_per_beat * numerator


class TimeSignature:
    def __init__(self, ticks_per_beat, numerator, denominator) -> None:
        super().__init__()
        self.numerator = numerator
        self.denominator = denominator
        self.bar_ticks = bar_ticks(ticks_per_beat, numerator, denominator)

    def within_bar(self, ticks):
        return ticks < self.bar_ticks

    def next_bar_start_delta(self, bar_tick):
        return self.bar_ticks - bar_tick


class Bar:
    def __init__(self, messages) -> None:
        super().__init__()
        self.messages = messages

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Bar):
            raise TypeError('can\'t compare message to {}'.format(type(other)))
        return self.messages == other.messages

    def __repr__(self) -> str:
        return 'Bar([\n%s])' % (',\n'.join(str(m) for m in self.messages))
