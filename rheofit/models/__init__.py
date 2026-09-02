from . import carreau
from . import carreau_carreau
from . import herschel_bulkley
from . import power_law
from . import tc
from . import tc_carreau
from . import tccc

MODELS: dict = {
    "carreau": carreau,
    "carreau_carreau": carreau_carreau,
    "herschel_bulkley": herschel_bulkley,
    "power_law": power_law,
    "tc": tc,
    "tc_carreau": tc_carreau,
    "tccc": tccc,
}

__all__ = ["MODELS"]
