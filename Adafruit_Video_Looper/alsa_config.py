import re

def parse_hw_device(s):
    if not s:
        return None

    m = re.match("^(\d+),(\d+)$", s)

    if not m:
        raise RuntimeError('Invalid value for alsa hardware device: {}'.format(s))
    
    return tuple(map(int, m.group(1, 2)))
