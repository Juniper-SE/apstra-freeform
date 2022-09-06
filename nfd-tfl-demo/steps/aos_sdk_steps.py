import time

from helpers.payloads import (
    build_nodes_payload,
    build_links_payload,
    build_config_templates_payload,
    build_config_templates_assignments_payload,
    build_property_sets_payload
)

#from helpers.decorators import step
#from helpers.waits import wait_assert
#
# from aos.sdk.utils import with_async_state
# from netaddr import IPNetwork



class Context(object):
    def __init__(self):
        self.blueprint_id = None
        self.device_profiles = None


class AosSdkSteps(object):
    def __init__(self, testsession):
        self.client = testsession.get_aos_sdk_freeform()
        self.generator = testsession.get_aos_sdk_generator()
        self.context = Context()

    # def delete_blueprint(self, bp_id):
    #     """
    #     Delete a blueprint with given id.
    #     :param bp_id: id of the blueprint
    #     """
    #     self.client.blueprints[bp_id].delete()
    #     time.sleep(1)

    def print_apstra_version(self):
        """ Print Apstra version  """
        return self.client.version.get()

    def create_blueprint(self, data):
        """
        Create a blueprint with given name and settings.
        :param data: dictionary with blueprint settings
        (id, template id, ref design, etc.)
        :return: blueprint as a dictionary
        """
        bp_name = data['id']
        data["label"] = bp_name
        self.context.blueprint_id = data['id']
        return self.client.blueprints.create(data)

    def import_device_profiles(self, device_profiles):
        blueprint_id = self.context.blueprint_id
        time.sleep(1)
        client = self.client.blueprints[blueprint_id]
        client.device_profiles.import_(device_profiles)
        time.sleep(1)
        # saving into context, will need later
        imported_dps = client.device_profiles.list()
        self.context.device_profiles = \
            {dp['device_profile_id']: dp['id'] for dp in imported_dps}

    def populate_blueprint(self, tfl_json):
        blueprint_id = self.context.blueprint_id
        batch_api_payload = []

        # payload for systems
        device_profile = self.context.device_profiles['Juniper_vEX']
        batch_api_payload += build_nodes_payload(tfl_json, device_profile)

        # payload for links
        batch_api_payload += build_links_payload(tfl_json)

        # payloads to import config_templates
        batch_api_payload += build_config_templates_payload()

        # payloads assign config templates to all systems
        batch_api_payload += build_config_templates_assignments_payload(tfl_json)

        # payload for property-sets
        batch_api_payload += build_property_sets_payload(tfl_json)

        client = self.client.blueprints[blueprint_id]
        client.batch(batch_api_payload)

    def rearrange_map_nodes_from_geo_loc(self, tfl_json):
        pass