import openstack
import requests
import yaml
from enum import Enum
from shovel.config import settings
import logging


class PanelImagesState(Enum):
    MISSING = 0
    SYNCED = 1
    EXTRA = 2
    UNKNOWN = 3


class GlanceAPIAvailability(Enum):
    UNAVAILABLE = 0
    AVAILABLE = 1


class Glance():

    def __init__(self):
        self.__os_config = settings.get('os_config')
        self.__os_connection = self.__create_connection(**self.__os_config)
        self.__glance_api_availability, self.__glance_public_images = self.__get_glance_all_images_and_availability()
        self.__url_iac_images_file = settings.get('gitlab_info')['url_iac_images_file']
        self.__token_gitlab = settings.get('gitlab_info')['token']
        self.__ref_brabch = settings.get('gitlab_info')['branch']

    def __get_glance_all_images_and_availability(self):
        images = []
        try:
            images_resource_list = self.__os_connection.image.images(visibility='public')
            availability = GlanceAPIAvailability.AVAILABLE
        except Exception:
            logging.exception("Can not get list of images from glance API")
            availability = GlanceAPIAvailability.UNAVAILABLE
            return availability, None
        for image in images_resource_list:
            images.append(image)
        return availability, images

    def __get_iac_images_file(self):
        iac_panel_images = []
        try:
            r = requests.get(self.__url_iac_images_file, params={'ref': self.__ref_brabch}, headers={"PRIVATE-TOKEN": self.__token_gitlab})
            iac_file = yaml.load(r.content.decode(), Loader=yaml.FullLoader)
            iac_os_images = iac_file['iac_os_images']
            for image_name, parameters in iac_os_images.items():
                if self.__os_config['region_name'] not in parameters.get('exclude_dc', []) and (parameters['properties'].get('arVisibility', -1) == 1 or parameters['properties'].get('marketPlace', -1) == 1):
                    iac_panel_images.append(image_name)
        except Exception:
            logging.exception("Can not get panel IaC images from gitlab")
            iac_panel_images = None
        return iac_panel_images

    def __is_panel_image(self, image):
        if image.visibility == 'public' and image.properties.get('arVisibility', '1') == '1' and 'arMigrate' not in image.properties:
            return True
        elif image.visibility == 'public' and (image.properties.get('arVisibility', '0') == '0') and (image.properties.get('marketPlace', '-1') == '1') and 'arMigrate' not in image.properties:
            return True
        return False

    def __get_panel_images(self):
        panel_images = []
        if self.get_glance_api_availability() == GlanceAPIAvailability.UNAVAILABLE:
            panel_images = None
        else:
            for glance_image in self.__glance_public_images:
                if self.__is_panel_image(glance_image):
                    panel_images.append(glance_image.name)
        return panel_images

    def __create_connection(self, auth_url, region_name, project_name, username, password, user_domain, project_domain, interface, endpoint_type):
        return openstack.connect(
            auth_url=auth_url,
            project_name=project_name,
            username=username,
            password=password,
            region_name=region_name,
            user_domain_name=user_domain,
            project_domain_name=project_domain,
            interface=interface,
            endpoint_type=endpoint_type
        )

    def get_glance_api_availability(self):
        return self.__glance_api_availability

    def check_panel_images_synchronization(self):
        panel_images = self.__get_panel_images()
        if self.get_glance_api_availability() == GlanceAPIAvailability.UNAVAILABLE:
            return PanelImagesState.UNKNOWN
        else:
            set_panel = set(panel_images)
            if len(set_panel) != len(panel_images):
                return PanelImagesState.EXTRA
            iac_panel_images = self.__get_iac_images_file()
            if iac_panel_images is not None:
                set_iac = set(iac_panel_images)
                if set_panel == set_iac:
                    return PanelImagesState.SYNCED
                set_diff = set_panel.difference(set_iac)
                if len(set_diff) != 0:
                    return PanelImagesState.EXTRA
                else:
                    return PanelImagesState.MISSING
            else:
                return PanelImagesState.UNKNOWN
