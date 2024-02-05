from dataclasses import dataclass
from dcs.forcedoptions import ForcedOptions
from dcs.mission import Mission


@dataclass
class MapLimiter:
    m: Mission

    def limit_map(self) -> None:
        m = self.m
        m.forced_options.options_view = ForcedOptions.Views.OnlyMap
