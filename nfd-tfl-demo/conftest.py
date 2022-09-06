import pytest

from testsession import TestSession
from steps.aos_sdk_steps import AosSdkSteps


def pytest_addoption(parser):
    parser.addoption("--config-path", action="store", default="config.yaml")


@pytest.fixture(scope="session", autouse=True)
def test_session(request):
    ts = TestSession(request.config.option.config_path)
    yield ts


@pytest.fixture(scope="module")
def aos_sdk_steps(test_session):
    yield AosSdkSteps(test_session)
