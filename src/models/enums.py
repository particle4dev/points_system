from enum import Enum

class ProtocolType(str, Enum):
    """ High-level category of the protocol for application logic. """
    DEX_UNISWAPV3 = "DEX_UNISWAPV3"
    LENDING_HYPURRFI = "LENDING_HYPURRFI"
    YIELD_PENDLE = "YIELD_PENDLE"

class QuantityType(str, Enum):
    """ The specific type of financial activity that earns points. """
    LP = "LP"
    YT = "YT"
    BORROW = "BORROW"
