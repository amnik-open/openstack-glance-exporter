from prometheus_client import Gauge
from .glance import Glance
from shovel import Shovel


class GlanceExporter(Shovel):
    glance_api = Gauge('glance_api_availability', 'Check state of glance api', ['status'])
    panel_images = Gauge('glance_panel_images_sync', 'Check if images on panel synced with IaC', ['state'])

    def probe(self):
        glance = Glance()
        panel_images_state = glance.check_panel_images_synchronization()
        glance_api_availability = glance.get_glance_api_availability()
        self.glance_api.labels(glance_api_availability.name).set(glance_api_availability.value)
        self.panel_images.labels(panel_images_state.name).set(panel_images_state.value)
