import os

from helpers.decorators import step
from helpers.waits import wait_assert

from aos.sdk.utils import with_async_state
from netaddr import IPNetwork


class AosSdkSteps(object):

    def __init__(self, testsession):
        self.client = testsession.get_aos_sdk_two_stage_l3clos()
        self.generator = testsession.get_aos_sdk_generator()

    @step("Deleting blueprint with id: '{1}'")
    def delete_blueprint(self, bp_id):
        """
        Delete a blueprint with given id.
        :param bp_id: id of the blueprint
        """
        self.client.blueprints[bp_id].delete()
        wait_assert(
            lambda: bp_id not in [
                bp["id"] for bp in self.client.blueprints.list()
            ], "Blueprint {} was not deleted".format(bp_id),
            check_count=10, sleep_time=1
        )

    @step("Printing version")
    def print_apstra_version(self):
        """ Print Apstra version  """
        return self.client.version.get()

    @step("Creating blueprint with name: '{1}'")
    def create_blueprint(self, bp_name, data):
        """
        Create a blueprint with given name and settings.
        :param bp_name: name of the created blueprint
        :param data: dictionary with blueprint settings
        (id, template id, ref design, etc.)
        :return: blueprint as a dictionary
        """
        data["label"] = bp_name
        return self.client.blueprints.create(data)


