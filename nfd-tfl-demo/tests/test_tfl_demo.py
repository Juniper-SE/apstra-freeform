import pytest
import uuid


@pytest.mark.dependency()
def test_print_apstra_version(aos_sdk_steps):
    """
    Ensures we can talk to Apstra VM via REST APIs
    """
    assert aos_sdk_steps.print_apstra_version()


@pytest.mark.skip(reason="Skipped by default, be careful with this one...")
@pytest.mark.dependency()
def test_remove_existing_resources(aos_sdk_steps):
    """
    Remove all existing blueprints.
    """
    aos_sdk_steps.delete_blueprints()


@pytest.mark.dependency()
def test_create_blueprint(aos_sdk_steps):
    """
    Initiate a freeform blueprint
    """

    def gen_name(prefix):
        return prefix + str(uuid.uuid4())[:8]

    data = dict(
        id=gen_name("freeform-"),
        design='freeform',
        init_type='default',
    )
    aos_sdk_steps.create_blueprint(data)


@pytest.mark.dependency()
def test_import_device_profiles(aos_sdk_steps):
    """

    Import Juniper_vEX device profile into the newly created blueprint
    """
    aos_sdk_steps.import_device_profiles(['Juniper_vEX'])


@pytest.mark.dependency()
def test_populate_blueprint(aos_sdk_steps, tfl_json):
    """
    Populate the blueprint modeling the London subway system entirely via
    batch APIs
    """
    aos_sdk_steps.populate_blueprint(tfl_json)


@pytest.mark.dependency()
def test_create_static_host_mappings(aos_sdk_steps):
    """
    This config template is a bit special, since it's created by querying AOS
    """
    aos_sdk_steps.create_static_host_mappings()

@pytest.mark.dependency()
def test_update_diagram_from_geo_location(aos_sdk_steps, tfl_json):
    """
    Override default node positioning by placing each node based on their latitude
    and longitude, thus making it prettier to look at
    """
    aos_sdk_steps.update_diagram_from_geo_location(tfl_json)