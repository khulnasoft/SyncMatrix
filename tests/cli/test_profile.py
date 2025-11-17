from uuid import uuid4

import pytest
import respx
from httpx import Response

from syncmatrix.context import use_profile
from syncmatrix.settings import (
    DEFAULT_PROFILES_PATH,
    SYNCMATRIX_API_KEY,
    SYNCMATRIX_DEBUG_MODE,
    SYNCMATRIX_PROFILES_PATH,
    Profile,
    ProfilesCollection,
    load_profiles,
    save_profiles,
    temporary_settings,
)
from syncmatrix.testing.cli import invoke_and_assert


@pytest.fixture(autouse=True)
def temporary_profiles_path(tmp_path):
    path = tmp_path / "profiles.toml"
    with temporary_settings({SYNCMATRIX_PROFILES_PATH: path}):
        yield path


def test_use_profile_unknown_key():
    invoke_and_assert(
        ["profile", "use", "foo"],
        expected_code=1,
        expected_output="Profile 'foo' not found.",
    )


class TestChangingProfileAndCheckingOrionConnection:
    @pytest.fixture
    def profiles(self):
        syncmatrix_cloud_api_url = "https://mock-cloud.khulnasoft.com/api"
        syncmatrix_cloud_orion_api_url = (
            f"{syncmatrix_cloud_api_url}/accounts/{uuid4()}/workspaces/{uuid4()}"
        )
        hosted_orion_api_url = "https://hosted-orion.khulnasoft.com/api"

        return ProfilesCollection(
            profiles=[
                Profile(
                    name="syncmatrix-cloud",
                    settings={
                        "SYNCMATRIX_API_URL": syncmatrix_cloud_orion_api_url,
                        "SYNCMATRIX_API_KEY": "a working cloud api key",
                    },
                ),
                Profile(
                    name="syncmatrix-cloud-with-invalid-key",
                    settings={
                        "SYNCMATRIX_API_URL": syncmatrix_cloud_orion_api_url,
                        "SYNCMATRIX_API_KEY": "a broken cloud api key",
                    },
                ),
                Profile(
                    name="hosted-orion",
                    settings={
                        "SYNCMATRIX_API_URL": hosted_orion_api_url,
                    },
                ),
                Profile(
                    name="ephemeral-syncmatrix",
                    settings={},
                ),
            ],
            active=None,
        )

    @pytest.fixture
    def authorized_cloud(self):
        # attempts to reach the Cloud 2 workspaces endpoint implies a good connection
        # to Syncmatrix Cloud as opposed to a hosted Syncmatrix server instance
        with respx.mock:
            authorized = respx.get(
                "https://mock-cloud.khulnasoft.com/api/me/workspaces",
            ).mock(return_value=Response(200, json=[]))

            yield authorized

    @pytest.fixture
    def unauthorized_cloud(self):
        # requests to cloud with an invalid key will result in a 401 response
        with respx.mock:
            unauthorized = respx.get(
                "https://mock-cloud.khulnasoft.com/api/me/workspaces",
            ).mock(return_value=Response(401, json={}))

            yield unauthorized

    @pytest.fixture
    def unhealthy_cloud(self):
        # Cloud may respond with a 500 error when having connection issues
        with respx.mock:
            unhealthy_cloud = respx.get(
                "https://mock-cloud.khulnasoft.com/api/me/workspaces",
            ).mock(return_value=Response(500, json={}))

            yield unhealthy_cloud

    @pytest.fixture
    def hosted_orion_has_no_cloud_api(self):
        # if the API URL points to a hosted Syncmatrix server instance, no Cloud API will be found
        with respx.mock:
            hosted = respx.get(
                "https://hosted-orion.khulnasoft.com/api/me/workspaces",
            ).mock(return_value=Response(404, json={}))

            yield hosted

    @pytest.fixture
    def healthy_hosted_orion(self):
        with respx.mock:
            hosted = respx.get(
                "https://hosted-orion.khulnasoft.com/api/health",
            ).mock(return_value=Response(200, json={}))

            yield hosted

    def connection_error(self, *args):
        raise Exception

    @pytest.fixture
    def unhealthy_hosted_orion(self):
        with respx.mock:
            badly_hosted = respx.get(
                "https://hosted-orion.khulnasoft.com/api/health",
            ).mock(side_effect=self.connection_error)

            yield badly_hosted

    def test_authorized_cloud_connection(self, authorized_cloud, profiles):
        save_profiles(profiles)
        invoke_and_assert(
            ["profile", "use", "syncmatrix-cloud"],
            expected_output_contains=(
                "Connected to Syncmatrix Cloud using profile 'syncmatrix-cloud'"
            ),
            expected_code=0,
        )

        profiles = load_profiles()
        assert profiles.active_name == "syncmatrix-cloud"

    def test_unauthorized_cloud_connection(self, unauthorized_cloud, profiles):
        save_profiles(profiles)
        invoke_and_assert(
            ["profile", "use", "syncmatrix-cloud-with-invalid-key"],
            expected_output_contains=(
                "Error authenticating with Syncmatrix Cloud using profile"
                " 'syncmatrix-cloud-with-invalid-key'"
            ),
            expected_code=1,
        )

        profiles = load_profiles()
        assert profiles.active_name == "syncmatrix-cloud-with-invalid-key"

    def test_unhealthy_cloud_connection(self, unhealthy_cloud, profiles):
        save_profiles(profiles)
        invoke_and_assert(
            ["profile", "use", "syncmatrix-cloud"],
            expected_output_contains="Error connecting to Syncmatrix Cloud",
            expected_code=1,
        )

        profiles = load_profiles()
        assert profiles.active_name == "syncmatrix-cloud"

    def test_using_hosted_orion(
        self, hosted_orion_has_no_cloud_api, healthy_hosted_orion, profiles
    ):
        save_profiles(profiles)
        invoke_and_assert(
            ["profile", "use", "hosted-orion"],
            expected_output_contains=(
                "Connected to Syncmatrix server using profile 'hosted-orion'"
            ),
            expected_code=0,
        )

        profiles = load_profiles()
        assert profiles.active_name == "hosted-orion"

    def test_unhealthy_hosted_orion(
        self, hosted_orion_has_no_cloud_api, unhealthy_hosted_orion, profiles
    ):
        save_profiles(profiles)
        invoke_and_assert(
            ["profile", "use", "hosted-orion"],
            expected_output_contains="Error connecting to Syncmatrix server",
            expected_code=1,
        )

        profiles = load_profiles()
        assert profiles.active_name == "hosted-orion"

    def test_using_ephemeral_orion(self, profiles):
        save_profiles(profiles)
        invoke_and_assert(
            ["profile", "use", "ephemeral-syncmatrix"],
            expected_output_contains=(
                "No Syncmatrix server specified using profile 'ephemeral-syncmatrix'"
            ),
            expected_code=0,
        )

        profiles = load_profiles()
        assert profiles.active_name == "ephemeral-syncmatrix"


def test_ls_default_profiles():
    # 'default' is not the current profile because we have a temporary profile in-use
    # during tests

    invoke_and_assert(["profile", "ls"], expected_output_contains="default")


def test_ls_additional_profiles():
    # 'default' is not the current profile because we have a temporary profile in-use
    # during tests

    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(name="foo", settings={}),
                Profile(name="bar", settings={}),
            ],
            active=None,
        )
    )

    invoke_and_assert(
        ["profile", "ls"],
        expected_output_contains=(
            "default",
            "foo",
            "bar",
        ),
    )


def test_ls_respects_current_from_profile_flag():
    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(name="foo", settings={}),
            ],
            active=None,
        )
    )

    invoke_and_assert(
        ["--profile", "foo", "profile", "ls"],
        expected_output_contains=(
            "default",
            "* foo",
        ),
    )


def test_ls_respects_current_from_context():
    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(name="foo", settings={}),
                Profile(name="bar", settings={}),
            ],
            active=None,
        )
    )

    with use_profile("bar"):
        invoke_and_assert(
            ["profile", "ls"],
            expected_output_contains=(
                "default",
                "foo",
                "* bar",
            ),
        )


def test_create_profile():
    invoke_and_assert(
        ["profile", "create", "foo"],
        expected_output="""
            Created profile with properties:
                name - 'foo'
                from name - None

            Use created profile for future, subsequent commands:
                syncmatrix profile use 'foo'

            Use created profile temporarily for a single command:
                syncmatrix -p 'foo' config view
            """,
    )

    profiles = load_profiles()
    assert profiles["foo"] == Profile(
        name="foo", settings={}, source=SYNCMATRIX_PROFILES_PATH.value()
    )


def test_create_profile_from_existing():
    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(name="foo", settings={SYNCMATRIX_API_KEY: "foo"}),
            ],
            active=None,
        )
    )

    invoke_and_assert(
        ["profile", "create", "bar", "--from", "foo"],
        expected_output="""
            Created profile with properties:
                name - 'bar'
                from name - foo

            Use created profile for future, subsequent commands:
                syncmatrix profile use 'bar'

            Use created profile temporarily for a single command:
                syncmatrix -p 'bar' config view
            """,
    )

    profiles = load_profiles()
    assert profiles["foo"].settings == {SYNCMATRIX_API_KEY: "foo"}, "Foo is unchanged"
    assert profiles["bar"] == Profile(
        name="bar",
        settings={SYNCMATRIX_API_KEY: "foo"},
        source=SYNCMATRIX_PROFILES_PATH.value(),
    )


def test_create_profile_from_unknown_profile():
    invoke_and_assert(
        ["profile", "create", "bar", "--from", "foo"],
        expected_output="Profile 'foo' not found.",
        expected_code=1,
    )


def test_create_profile_with_existing_profile():
    invoke_and_assert(
        ["profile", "create", "default"],
        expected_output="""
            Profile 'default' already exists.
            To create a new profile, remove the existing profile first:

                syncmatrix profile delete 'default'
            """,
        expected_code=1,
    )


def test_delete_profile():
    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(name="foo", settings={SYNCMATRIX_API_KEY: "foo"}),
                Profile(name="bar", settings={SYNCMATRIX_API_KEY: "bar"}),
            ],
            active=None,
        )
    )

    invoke_and_assert(
        ["profile", "delete", "bar"], expected_output="Removed profile 'bar'."
    )

    profiles = load_profiles()
    assert "foo" in profiles
    assert "bar" not in profiles


def test_delete_profile_default_is_reset():
    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(name="default", settings={SYNCMATRIX_API_KEY: "foo"}),
            ],
            active=None,
        )
    )

    invoke_and_assert(
        ["profile", "delete", "default"], expected_output="Reset profile 'default'."
    )

    profiles = load_profiles()
    assert profiles["default"] == Profile(
        name="default",
        settings={},
        source=DEFAULT_PROFILES_PATH,
    )


def test_delete_profile_unknown_name():
    invoke_and_assert(
        ["profile", "delete", "foo"],
        expected_output="Profile 'foo' not found.",
        expected_code=1,
    )


def test_delete_profile_cannot_target_active_profile():
    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(name="foo", settings={SYNCMATRIX_API_KEY: "foo"}),
            ],
            active=None,
        )
    )

    with use_profile("foo"):
        invoke_and_assert(
            ["profile", "delete", "foo"],
            expected_output=(
                "Profile 'foo' is the active profile. You must switch profiles before"
                " it can be deleted."
            ),
            expected_code=1,
        )


def test_rename_profile_name_exists():
    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(name="foo", settings={}),
                Profile(name="bar", settings={}),
            ],
            active=None,
        )
    )

    invoke_and_assert(
        ["profile", "rename", "foo", "bar"],
        expected_output="Profile 'bar' already exists.",
        expected_code=1,
    )


def test_rename_profile_unknown_name():
    invoke_and_assert(
        ["profile", "rename", "foo", "bar"],
        expected_output="Profile 'foo' not found.",
        expected_code=1,
    )


def test_rename_profile_renames_profile():
    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(name="foo", settings={SYNCMATRIX_API_KEY: "foo"}),
            ],
            active=None,
        )
    )

    invoke_and_assert(
        ["profile", "rename", "foo", "bar"],
        expected_output="Renamed profile 'foo' to 'bar'.",
        expected_code=0,
    )

    profiles = load_profiles()
    assert "foo" not in profiles, "The original profile should not exist anymore"
    assert profiles["bar"].settings == {
        SYNCMATRIX_API_KEY: "foo"
    }, "Settings should be retained"
    assert profiles.active_name != "bar", "The active profile should not be changed"


def test_rename_profile_changes_active_profile():
    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(name="foo", settings={SYNCMATRIX_API_KEY: "foo"}),
            ],
            active="foo",
        )
    )

    invoke_and_assert(
        ["profile", "rename", "foo", "bar"],
        expected_output="Renamed profile 'foo' to 'bar'.",
        expected_code=0,
    )

    profiles = load_profiles()
    assert profiles.active_name == "bar"


def test_rename_profile_warns_on_environment_variable_active_profile(monkeypatch):
    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(name="foo", settings={SYNCMATRIX_API_KEY: "foo"}),
            ],
            active=None,
        )
    )

    monkeypatch.setenv("SYNCMATRIX_PROFILE", "foo")

    invoke_and_assert(
        ["profile", "rename", "foo", "bar"],
        expected_output_contains=(
            "You have set your current profile to 'foo' with the SYNCMATRIX_PROFILE "
            "environment variable. You must update this variable to 'bar' "
            "to continue using the profile."
        ),
        expected_code=0,
    )

    profiles = load_profiles()
    assert (
        profiles.active_name != "foo"
    ), "The active profile should not be updated in the file"


def test_inspect_profile_unknown_name():
    invoke_and_assert(
        ["profile", "inspect", "foo"],
        expected_output="Profile 'foo' not found.",
        expected_code=1,
    )


def test_inspect_profile():
    save_profiles(
        ProfilesCollection(
            profiles=[
                Profile(
                    name="foo",
                    settings={SYNCMATRIX_API_KEY: "foo", SYNCMATRIX_DEBUG_MODE: True},
                ),
            ],
            active=None,
        )
    )

    invoke_and_assert(
        ["profile", "inspect", "foo"],
        expected_output="""
            SYNCMATRIX_API_KEY='foo'
            SYNCMATRIX_DEBUG_MODE='True'
            """,
    )


def test_inspect_profile_without_settings():
    save_profiles(
        ProfilesCollection(
            profiles=[Profile(name="foo", settings={})],
            active=None,
        )
    )

    invoke_and_assert(
        ["profile", "inspect", "foo"],
        expected_output="""
            Profile 'foo' is empty.
            """,
    )
