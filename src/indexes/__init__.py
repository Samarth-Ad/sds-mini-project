from src.indexes.forward_index import ForwardIndex
from src.indexes.inverted_index import InvertedIndex
from src.indexes.positional_inverted_index import PositionalInvertedIndex
from src.indexes.sequential_scan import SequentialScan

STRATEGIES = {
    "sequential": SequentialScan,
    "forward": ForwardIndex,
    "inverted": InvertedIndex,
    "positional": PositionalInvertedIndex,
}
