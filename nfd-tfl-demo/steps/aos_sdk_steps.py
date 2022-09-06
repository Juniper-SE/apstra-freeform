import time

from helpers.payloads import (
    build_nodes_payload,
    build_links_payload,
    build_config_templates_payload,
    build_config_templates_assignments_payload,
    build_property_sets_payload
)

from helpers.map_utils import lat_long_to_screen_x_y


class Context(object):
    def __init__(self):
        self.blueprint_id = None
        self.device_profiles = None


class AosSdkSteps(object):
    def __init__(self, testsession):
        self.client = testsession.get_aos_sdk_freeform()
        self.generator = testsession.get_aos_sdk_generator()
        self.context = Context()

    def delete_blueprints(self):
        """
        Delete a blueprint with given id.
        :param bp_id: id of the blueprint
        """
        for bp_id in [bp['id'] for bp in self.client.blueprints.list()]:
            self.client.blueprints[bp_id].delete()


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

    def update_diagram_from_geo_location(self, tfl_json):
        """ Creates/updates user preferences (Topology diagrams)
            for the freeform blueprint based on latitude/longitude
            information in tfl.json.
        """
        time.sleep(10)
        blueprint_id = self.context.blueprint_id
        client = self.client.blueprints[blueprint_id]

        system_labels_to_ids = {
            s['label']: s['id'] for s in client.systems.list()}

        new_prefs = {}
        for station in tfl_json['stations']:
            lat, lng = float(station['latitude']), float(station['longitude'])
            x, y = lat_long_to_screen_x_y(lat, lng)
            node_id = system_labels_to_ids[station['name']]
            new_prefs[node_id] = '[%s, %s, %s]' % (x, y, station['zone'])

        client.preferences.update(data={'preferences': {'userData': new_prefs}})
