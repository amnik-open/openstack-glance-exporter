from shovel import ShovelStartMode
from src.prober import GlanceExporter

GlanceExporter().start(ShovelStartMode.PER_REQUEST, reset_metrics=True)
