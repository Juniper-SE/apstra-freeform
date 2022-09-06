import pytest
import uuid

def gen_name(prefix):
    return prefix + str(uuid.uuid4())[:8]


@pytest.mark.dependency()
def test_print_apstra_version(aos_sdk_steps):
     assert aos_sdk_steps.print_apstra_version()

# @pytest.mark.dependency()
# def test_remove_existing_resources(aos_sdk_steps):
#      aos_sdk_steps.delete_blueprint('freeform_blueprint')

@pytest.mark.dependency()
def test_create_blueprint(aos_sdk_steps):
     data = dict(
          id=gen_name("freeform-"),
          design='freeform',
          init_type='default',
     )
     aos_sdk_steps.create_blueprint(data)

@pytest.mark.dependency()
def test_import_device_profiles(aos_sdk_steps):
     aos_sdk_steps.import_device_profiles(['Juniper_vEX'])


@pytest.mark.dependency()
def test_populate_blueprint(aos_sdk_steps, tfl_json):
     aos_sdk_steps.populate_blueprint(tfl_json)

@pytest.mark.dependency()
def test_beautify_map(aos_sdk_steps, tfl_json):
     aos_sdk_steps.rearrange_map_nodes_from_geo_loc(tfl_json)