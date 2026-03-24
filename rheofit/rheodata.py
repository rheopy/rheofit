from importlib.resources import files
from tadatakit.classes import Experiment


_DATASETS = {
    "cp2pc_pg": "cp2pc_pg.json",
    "HA1pc_water":"HA1pc_water.json"
}


def __getattr__(name):
    """Lazy-load JSON data files as Experiment objects."""
    if name in _DATASETS:
        data_path = files("rheofit.data").joinpath(_DATASETS[name])
        experiment = Experiment.from_json(str(data_path))
        globals()[name] = experiment
        return experiment
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

if __name__ == "__main__":
    print('ok')
    pass
