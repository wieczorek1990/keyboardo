"""Fit complete practice groups into rows with Return markers."""


def layout_exercise(target, width, measure):
    """Wrap whole groups, reserving space for the visible Return marker."""
    row_breaks = set()
    line = ""
    offset = 0
    for group in target.rstrip("\n").split(" "):
        candidate = line + (" " if line else "") + group
        if line and measure(candidate + " ↵") > width:
            row_breaks.add(offset - 1)
            line = group
        else:
            line = candidate
        offset += len(group) + 1
    display = []
    display_offsets = []
    length = 0
    for index, char in enumerate(target):
        display_offsets.append(length)
        if index in row_breaks:
            value = "↵\n"
        elif char == "\n":
            value = "↵"
        else:
            value = char
        display.append(value)
        length += len(value)
    display_offsets.append(length)
    return "".join(display), display_offsets, row_breaks
