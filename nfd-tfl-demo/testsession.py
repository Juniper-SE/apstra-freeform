import yaml

from aos.sdk.reference_design.client_registry import CLIENT_REGISTRY
import aos.sdk.generator as g


class TestSession(object):
    test_session = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.test_session, cls):
            cls.test_session = object.__new__(cls)
        return cls.test_session

    def __init__(self, config):
        self.__aos_sdk_clients = {}
        self.__aos_sdk_generator = None
        with open(config) as yaml_file:
            self.config = yaml.safe_load(yaml_file)

    def get_aos_sdk_two_stage_l3clos(self):
        if "two_stage_l3_clos" not in self.__aos_sdk_clients:
            self.__aos_sdk_clients["two_stage_l3_clos"] = CLIENT_REGISTRY[
                "two_stage_l3clos"
            ].Client(self.config["url"], verify_certificates=False)
            self.__aos_sdk_clients["two_stage_l3_clos"].login()
        return self.__aos_sdk_clients["two_stage_l3_clos"]

    def get_aos_sdk_freeform(self):
        if "freeform" not in self.__aos_sdk_clients:
            self.__aos_sdk_clients["freeform"] = CLIENT_REGISTRY[
                "freeform"
            ].Client(self.config["url"], verify_certificates=False)
            self.__aos_sdk_clients["freeform"].login()
        return self.__aos_sdk_clients["freeform"]

    def get_aos_sdk_generator(self):
        if not self.__aos_sdk_generator:
            self.__aos_sdk_generator = g
        return self.__aos_sdk_generator
