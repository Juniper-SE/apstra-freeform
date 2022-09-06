import pytest

@pytest.mark.dependency()
def test_print_apstra_version(aos_sdk_steps):
     assert aos_sdk_steps.print_apstra_version()

@pytest.mark.dependency()
def test_remove_existing_resources(aos_sdk_steps):
     aos_sdk_steps.delete_blueprint('freeform_blueprint')

@pytest.mark.dependency()
def test_create_blueprint(aos_sdk_steps):
     data = dict(
          id='freeform_blueprint',
          design='freeform',
          init_type='default',
     )
     aos_sdk_steps.create_blueprint('freeform_blueprint', data)

