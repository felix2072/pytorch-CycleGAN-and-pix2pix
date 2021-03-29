from spout.sources import FileInputStream
from spout.structs import Function, Predicate
from spout.outputs import PrintOperation


class StartsWithDigit(Predicate):
    def test(self, obj):
        return obj[0].is_digit()


class StripFirstChar(Function):
    def apply(self, input):
        return input[1:]


s = FileInputStream("test.txt")
s \
    .filter(StartsWithDigit()) \
    .map(StripFirstChar()) \
    .for_each(PrintOperation())