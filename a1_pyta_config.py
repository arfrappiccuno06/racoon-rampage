import python_ta.contracts
# note: this is imported by a1.py
from python_ta.contracts import check_contracts

python_ta.contracts.ENABLE_CONTRACT_CHECKING = True

pyta_config = {
    "allowed-io": [],
    "allowed-import-modules": [
        "doctest",
        "python_ta",
        "typing",
        "random",
        "__future__",
        "python_ta.contracts",
        "a1_pyta_config",
        "math"
    ],
    "disable": [
        "E1136"
    ],
    "max-attributes": 15,
    "max-line-length": 120,
    "max-module-lines": 1600
}
