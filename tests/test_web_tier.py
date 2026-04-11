from pathlib import Path

import pytest

import app as app_package
from app import create_app
from app.databases.dao_mysql import MySQLDatabase
from app.databases.dao_sqllite import SQLiteDatabase


def _build_test_dao(flask_app):
    """Create a DAO instance using the same request-time factory configuration as the app."""
    dao_factory = flask_app.extensions["dao_factory"]
    dao = dao_factory["class"](**dao_factory["kwargs"])
    code, err, _ = dao.connect()
    assert code == 0, err
    return dao


def _session_csrf(client):
    """Return the current CSRF token stored in the session."""
    with client.session_transaction() as session_state:
        return session_state["csrf_token"]


def _login(client):
    """Log in through the real form flow and return the redirect response."""
    client.get("/login")
    return client.post(
        "/login",
        data={
            "csrf_token": _session_csrf(client),
            "username": "Test User",
            "password": "secret",
        },
        follow_redirects=False,
    )


def _set_context(client, workflow_id):
    """Activate a workflow context through the real form flow."""
    return client.post(
        "/set-context",
        data={"csrf_token": _session_csrf(client), "workflow_id": workflow_id},
        follow_redirects=False,
    )


@pytest.fixture
def flask_app(tmp_path):
    """Create an isolated Flask app backed by a temporary SQLite file."""
    db_path = Path(tmp_path) / "web_tier.sqlite3"
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "DB_NAME": "web_tier_test",
            "DB_URL": f"sqlite:///{db_path.as_posix()}",
        }
    )
    return app


@pytest.fixture
def client(flask_app):
    """Return the Flask test client for the configured app."""
    return flask_app.test_client()


def test_create_app_honors_sqlite_backend_override(tmp_path):
    db_path = Path(tmp_path) / "override.sqlite3"
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "DB_BACKEND": "sqlite",
            "DB_NAME": "override_test",
            "DB_URL": f"sqlite:///{db_path.as_posix()}",
            "DB_HOST": None,
            "DB_USER": None,
            "DB_PASSWORD": None,
        }
    )

    dao_factory = app.extensions["dao_factory"]
    assert dao_factory["class"] is SQLiteDatabase
    assert Path(dao_factory["kwargs"]["db_path"]) == db_path.resolve()


def test_create_app_resolves_relative_sqlite_path_to_absolute_location():
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "DB_BACKEND": "sqlite",
            "DB_NAME": "relative_test",
            "DB_URL": "sqlite:///relative_test.sqlite3",
        }
    )

    dao_factory = app.extensions["dao_factory"]
    expected_path = Path(app_package.__file__).resolve().parent.parent / "relative_test.sqlite3"
    assert dao_factory["class"] is SQLiteDatabase
    assert Path(dao_factory["kwargs"]["db_path"]) == expected_path.resolve()


def test_dashboard_redirects_to_login_when_unauthenticated(client):
    response = client.get("/dashboard/workflows", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_login_sets_session_and_redirects_to_workflow_selection(client):
    response = _login(client)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/select-workflow")

    with client.session_transaction() as session_state:
        assert session_state["logged_in"] is True
        assert session_state["username"] == "Test User"


def test_select_workflow_page_shows_logoff_option(client):
    _login(client)

    response = client.get("/select-workflow")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Log off" in page
    assert "/logout" in page


def test_select_workflow_page_offers_create_form_when_empty(client):
    _login(client)

    response = client.get("/select-workflow")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Create first workflow" in page
    assert "/select-workflow/create" in page


def test_logged_in_user_without_context_redirects_to_workflow_selection(client):
    _login(client)

    response = client.get("/dashboard/roles", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/select-workflow")


def test_select_workflow_shows_database_error_when_mysql_config_is_incomplete(client, flask_app):
    flask_app.extensions["dao_factory"] = {
        "class": MySQLDatabase,
        "kwargs": {
            "host": None,
            "user": None,
            "password": None,
            "dbname": None,
            "port": 3306,
            "auth_plugin": "mysql_native_password",
        },
    }

    _login(client)
    response = client.get("/select-workflow")
    page = response.get_data(as_text=True)

    assert response.status_code == 503
    assert "MySQL configuration is incomplete" in page
    assert "Missing: host, user, password, dbname" in page


def test_workflow_selection_sets_active_context(client, flask_app):
    dao = _build_test_dao(flask_app)
    _, _, workflow_id = dao.insert_into_workflow_table(
        "Project Intake",
        "Intake workflow",
        "Operations",
        "Default",
        "tester",
    )
    dao.close()

    _login(client)
    response = _set_context(client, workflow_id)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard/workflows")

    with client.session_transaction() as session_state:
        assert session_state["workflow_id"] == workflow_id
        assert session_state["workflow_name"] == "Project Intake"


def test_dashboard_shows_logoff_option_when_logged_in(client, flask_app):
    dao = _build_test_dao(flask_app)
    _, _, workflow_id = dao.insert_into_workflow_table(
        "Logoff Workflow",
        "Workflow for dashboard logoff action",
        "Operations",
        "Primary",
        "tester",
    )
    dao.close()

    _login(client)
    _set_context(client, workflow_id)

    response = client.get("/dashboard/workflows")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Log off" in page
    assert "/logout" in page


def test_help_endpoint_requires_authentication(client):
    response = client.get("/help/context-roles")

    assert response.status_code == 401
    assert response.get_json() == {"error": "Authentication required."}


def test_help_endpoint_requires_workflow_context(client):
    _login(client)

    response = client.get("/help/context-roles")

    assert response.status_code == 428
    assert response.get_json() == {"error": "Workflow context required."}


def test_create_workflow_from_selection_sets_context_and_redirects(client):
    _login(client)

    response = client.post(
        "/select-workflow/create",
        data={
            "csrf_token": _session_csrf(client),
            "workflow_name": "First Workflow",
            "workflow_description": "Created before selection",
            "workflow_type": "Operations",
            "workflow_subtype": "Primary",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard/workflows")

    with client.session_transaction() as session_state:
        assert session_state["workflow_name"] == "First Workflow"
        assert session_state["workflow_id"] is not None


def test_dashboard_exposes_context_help_topic_for_active_section(client, flask_app):
    dao = _build_test_dao(flask_app)
    _, _, workflow_id = dao.insert_into_workflow_table(
        "Help Workflow",
        "Workflow for help topic rendering",
        "Operations",
        "Primary",
        "tester",
    )
    dao.close()

    _login(client)
    _set_context(client, workflow_id)

    response = client.get("/dashboard/roles")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'data-help-open' in page
    assert 'data-help-topic="context-roles"' in page


def test_swap_workflow_clears_active_context_and_redirects(client, flask_app):
    dao = _build_test_dao(flask_app)
    _, _, workflow_id = dao.insert_into_workflow_table(
        "Swap Workflow",
        "Workflow for swap validation",
        "Operations",
        "Primary",
        "tester",
    )
    dao.close()

    _login(client)
    _set_context(client, workflow_id)

    response = client.get("/swap", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/select-workflow")

    with client.session_transaction() as session_state:
        assert "workflow_id" not in session_state
        assert "workflow_name" not in session_state


def test_help_endpoint_returns_rendered_html_for_known_topic(client, flask_app):
    dao = _build_test_dao(flask_app)
    _, _, workflow_id = dao.insert_into_workflow_table(
        "Known Help Workflow",
        "Workflow for known help topic",
        "Operations",
        "Primary",
        "tester",
    )
    dao.close()

    _login(client)
    _set_context(client, workflow_id)

    response = client.get("/help/context-roles")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["topic"] == "context-roles"
    assert payload["resolved_topic"] == "context-roles"
    assert payload["fallback"] is False
    assert "<h1>Roles</h1>" in payload["html"]


def test_help_endpoint_falls_back_to_index_for_missing_topic(client, flask_app):
    dao = _build_test_dao(flask_app)
    _, _, workflow_id = dao.insert_into_workflow_table(
        "Fallback Help Workflow",
        "Workflow for help fallback",
        "Operations",
        "Primary",
        "tester",
    )
    dao.close()

    _login(client)
    _set_context(client, workflow_id)

    response = client.get("/help/context-missing-topic")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["topic"] == "context-missing-topic"
    assert payload["resolved_topic"] == "index"
    assert payload["fallback"] is True
    assert "<h1>PDFA Help</h1>" in payload["html"]


def test_help_endpoint_rejects_invalid_topic(client, flask_app):
    dao = _build_test_dao(flask_app)
    _, _, workflow_id = dao.insert_into_workflow_table(
        "Invalid Help Workflow",
        "Workflow for invalid help topic",
        "Operations",
        "Primary",
        "tester",
    )
    dao.close()

    _login(client)
    _set_context(client, workflow_id)

    response = client.get("/help/..")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Invalid help topic."}


def test_logout_clears_session_and_redirects_to_login(client):
    _login(client)

    response = client.get("/logout", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")

    with client.session_transaction() as session_state:
        assert "logged_in" not in session_state
        assert "username" not in session_state
        assert "workflow_id" not in session_state
        assert "workflow_name" not in session_state


def test_roles_dashboard_only_shows_roles_for_active_workflow(client, flask_app):
    dao = _build_test_dao(flask_app)
    _, _, workflow_a = dao.insert_into_workflow_table(
        "Workflow A",
        "First workflow",
        "Operations",
        "Primary",
        "tester",
    )
    _, _, workflow_b = dao.insert_into_workflow_table(
        "Workflow B",
        "Second workflow",
        "Operations",
        "Primary",
        "tester",
    )
    dao.insert_into_role_table(workflow_a, "Approver", "Approves requests", "Human", "Primary", "tester")
    dao.insert_into_role_table(workflow_b, "Observer", "Reads requests", "Human", "Secondary", "tester")
    dao.close()

    _login(client)
    _set_context(client, workflow_a)

    response = client.get("/dashboard/roles")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Approver" in page
    assert "Observer" not in page


def test_role_create_form_uses_active_workflow_scope(client, flask_app):
    dao = _build_test_dao(flask_app)
    _, _, workflow_id = dao.insert_into_workflow_table(
        "Scoped Workflow",
        "Workflow for scoped role creation",
        "Operations",
        "Primary",
        "tester",
    )
    dao.close()

    _login(client)
    _set_context(client, workflow_id)
    response = client.post(
        "/dashboard/roles/save",
        data={
            "csrf_token": _session_csrf(client),
            "role_name": "Reviewer",
            "role_description": "Reviews submissions",
            "role_type": "Human",
            "role_subtype": "Secondary",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard/roles")

    verification_dao = _build_test_dao(flask_app)
    _, _, roles = verification_dao.select_all_from_role_table()
    verification_dao.close()

    matching_roles = [role for role in roles if role["role_name"] == "Reviewer"]
    assert len(matching_roles) == 1
    assert matching_roles[0]["workspace_id"] == workflow_id


def test_role_create_form_rejects_missing_csrf_token(client, flask_app):
    dao = _build_test_dao(flask_app)
    _, _, workflow_id = dao.insert_into_workflow_table(
        "CSRF Workflow",
        "Workflow for csrf validation",
        "Operations",
        "Primary",
        "tester",
    )
    dao.close()

    _login(client)
    _set_context(client, workflow_id)
    response = client.post(
        "/dashboard/roles/save",
        data={
            "role_name": "Rejected Reviewer",
            "role_description": "Should not be created",
            "role_type": "Human",
            "role_subtype": "Secondary",
        },
        follow_redirects=True,
    )

    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "session token expired" in page.lower()

    verification_dao = _build_test_dao(flask_app)
    _, _, roles = verification_dao.select_all_from_role_table()
    verification_dao.close()

    assert not [role for role in roles if role["role_name"] == "Rejected Reviewer"]


def test_roles_dashboard_empty_state_uses_single_create_action(client, flask_app):
    dao = _build_test_dao(flask_app)
    _, _, workflow_id = dao.insert_into_workflow_table(
        "Role Workflow",
        "Workflow for role empty state",
        "Operations",
        "Primary",
        "tester",
    )
    dao.close()

    _login(client)
    _set_context(client, workflow_id)

    response = client.get("/dashboard/roles")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "No roles exist for the active workflow yet." in page
    assert "Create Role" in page
    assert "Create first role" not in page


def test_guards_dashboard_empty_state_shows_create_affordance(client, flask_app):
    dao = _build_test_dao(flask_app)
    _, _, workflow_id = dao.insert_into_workflow_table(
        "Guard Workflow",
        "Workflow for guard empty state",
        "Operations",
        "Primary",
        "tester",
    )
    dao.close()

    _login(client)
    _set_context(client, workflow_id)

    response = client.get("/dashboard/guards")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "No guards exist for the active workflow yet." in page
    assert "Create Guard" in page
    assert "Create first guard" not in page


def test_guard_create_form_uses_active_workflow_scope(client, flask_app):
    dao = _build_test_dao(flask_app)
    _, _, workflow_id = dao.insert_into_workflow_table(
        "Guard Scope Workflow",
        "Workflow for scoped guard creation",
        "Operations",
        "Primary",
        "tester",
    )
    dao.close()

    _login(client)
    _set_context(client, workflow_id)
    response = client.post(
        "/dashboard/guards/save",
        data={
            "csrf_token": _session_csrf(client),
            "guard_name": "Approval Gate",
            "guard_description": "Checks approval preconditions",
            "guard_type": "Policy",
            "guard_subtype": "Default",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard/guards")

    verification_dao = _build_test_dao(flask_app)
    _, _, guards = verification_dao.select_all_from_guard_table()
    verification_dao.close()

    matching_guards = [guard for guard in guards if guard["guard_name"] == "Approval Gate"]
    assert len(matching_guards) == 1
    assert matching_guards[0]["workspace_id"] == workflow_id


def test_interactions_dashboard_empty_state_shows_create_affordance(client, flask_app):
    dao = _build_test_dao(flask_app)
    _, _, workflow_id = dao.insert_into_workflow_table(
        "Interaction Workflow",
        "Workflow for interaction empty state",
        "Operations",
        "Primary",
        "tester",
    )
    dao.close()

    _login(client)
    _set_context(client, workflow_id)

    response = client.get("/dashboard/interactions")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "No interactions exist for the active workflow yet." in page
    assert "Create Interaction" in page
    assert "Create first interaction" not in page


def test_interaction_create_form_uses_active_workflow_scope(client, flask_app):
    dao = _build_test_dao(flask_app)
    _, _, workflow_id = dao.insert_into_workflow_table(
        "Interaction Scope Workflow",
        "Workflow for scoped interaction creation",
        "Operations",
        "Primary",
        "tester",
    )
    dao.close()

    _login(client)
    _set_context(client, workflow_id)
    response = client.post(
        "/dashboard/interactions/save",
        data={
            "csrf_token": _session_csrf(client),
            "interaction_name": "Escalation Path",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard/interactions")

    verification_dao = _build_test_dao(flask_app)
    _, _, interactions = verification_dao.select_all_from_interaction_table()
    verification_dao.close()

    matching_interactions = [
        interaction for interaction in interactions if interaction["interaction_name"] == "Escalation Path"
    ]
    assert len(matching_interactions) == 1
    assert matching_interactions[0]["workflow_id"] == workflow_id


def test_interaction_components_dashboard_empty_state_shows_create_affordance(client, flask_app):
    dao = _build_test_dao(flask_app)
    _, _, workflow_id = dao.insert_into_workflow_table(
        "Component Workflow",
        "Workflow for interaction component empty state",
        "Operations",
        "Primary",
        "tester",
    )
    dao.close()

    _login(client)
    _set_context(client, workflow_id)

    response = client.get("/dashboard/interaction-components")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Create Interaction Component" in page
    assert "Create first interaction component" not in page


def test_interaction_components_dashboard_only_shows_active_workflow_data(client, flask_app):
    dao = _build_test_dao(flask_app)
    _, _, workflow_a = dao.insert_into_workflow_table(
        "Components A",
        "First component workflow",
        "Operations",
        "Primary",
        "tester",
    )
    _, _, workflow_b = dao.insert_into_workflow_table(
        "Components B",
        "Second component workflow",
        "Operations",
        "Primary",
        "tester",
    )
    _, _, role_a = dao.insert_into_role_table(workflow_a, "Reviewer A", "", "Human", "Primary", "tester")
    _, _, role_b = dao.insert_into_role_table(workflow_b, "Reviewer B", "", "Human", "Primary", "tester")
    _, _, guard_a = dao.insert_into_guard_table(workflow_a, "Guard A", "", "Policy", "Default", "tester")
    _, _, guard_b = dao.insert_into_guard_table(workflow_b, "Guard B", "", "Policy", "Default", "tester")
    _, _, interaction_a = dao.insert_into_interaction_table(workflow_a, "Interaction A", "tester")
    _, _, interaction_b = dao.insert_into_interaction_table(workflow_b, "Interaction B", "tester")
    dao.insert_into_interaction_component_table(
        "Component A",
        "Visible component",
        "Notification",
        "Email",
        interaction_a,
        guard_a,
        role_a,
        "outbound",
        "tester",
    )
    dao.insert_into_interaction_component_table(
        "Component B",
        "Hidden component",
        "Notification",
        "SMS",
        interaction_b,
        guard_b,
        role_b,
        "inbound",
        "tester",
    )
    dao.close()

    _login(client)
    _set_context(client, workflow_a)

    response = client.get("/dashboard/interaction-components")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Component A" in page
    assert "Interaction A" in page
    assert "Reviewer A" in page
    assert "Guard A" in page
    assert "Component B" not in page
    assert "Interaction B" not in page
    assert "Reviewer B" not in page
    assert "Guard B" not in page


def test_interaction_component_create_form_uses_active_workflow_scope(client, flask_app):
    dao = _build_test_dao(flask_app)
    _, _, workflow_id = dao.insert_into_workflow_table(
        "Component Scope Workflow",
        "Workflow for scoped component creation",
        "Operations",
        "Primary",
        "tester",
    )
    _, _, role_id = dao.insert_into_role_table(workflow_id, "Reviewer", "", "Human", "Primary", "tester")
    _, _, guard_id = dao.insert_into_guard_table(workflow_id, "Approval Gate", "", "Policy", "Default", "tester")
    _, _, interaction_id = dao.insert_into_interaction_table(workflow_id, "Escalation Path", "tester")
    dao.close()

    _login(client)
    _set_context(client, workflow_id)
    response = client.post(
        "/dashboard/interaction-components/save",
        data={
            "csrf_token": _session_csrf(client),
            "interaction_component_name": "Email Notice",
            "interaction_component_description": "Sends an outbound update",
            "interaction_component_type": "Notification",
            "interaction_component_subtype": "Email",
            "interaction_id": interaction_id,
            "role_id": role_id,
            "guard_id": guard_id,
            "direction": "outbound",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard/interaction-components")

    verification_dao = _build_test_dao(flask_app)
    _, _, components = verification_dao.select_all_from_interaction_component_table()
    verification_dao.close()

    matching_components = [
        component for component in components if component["interaction_component_name"] == "Email Notice"
    ]
    assert len(matching_components) == 1
    assert matching_components[0]["workflow_id"] == workflow_id
    assert matching_components[0]["interaction_id"] == interaction_id
    assert matching_components[0]["role_id"] == role_id
    assert matching_components[0]["guard_id"] == guard_id


def test_interaction_component_create_rejects_cross_workflow_relationships(client, flask_app):
    dao = _build_test_dao(flask_app)
    _, _, workflow_a = dao.insert_into_workflow_table(
        "Component Validation A",
        "First validation workflow",
        "Operations",
        "Primary",
        "tester",
    )
    _, _, workflow_b = dao.insert_into_workflow_table(
        "Component Validation B",
        "Second validation workflow",
        "Operations",
        "Primary",
        "tester",
    )
    _, _, interaction_id = dao.insert_into_interaction_table(workflow_a, "Interaction A", "tester")
    _, _, role_b = dao.insert_into_role_table(workflow_b, "Role B", "", "Human", "Primary", "tester")
    _, _, guard_b = dao.insert_into_guard_table(workflow_b, "Guard B", "", "Policy", "Default", "tester")
    dao.close()

    _login(client)
    _set_context(client, workflow_a)
    response = client.post(
        "/dashboard/interaction-components/save",
        data={
            "csrf_token": _session_csrf(client),
            "interaction_component_name": "Invalid Component",
            "interaction_component_description": "Should be rejected",
            "interaction_component_type": "Notification",
            "interaction_component_subtype": "Email",
            "interaction_id": interaction_id,
            "role_id": role_b,
            "guard_id": guard_b,
            "direction": "outbound",
        },
        follow_redirects=True,
    )

    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "does not belong to the active workflow" in page

    verification_dao = _build_test_dao(flask_app)
    _, _, components = verification_dao.select_all_from_interaction_component_table()
    verification_dao.close()

    assert not [component for component in components if component["interaction_component_name"] == "Invalid Component"]


def test_interaction_component_create_rejects_missing_csrf_token(client, flask_app):
    dao = _build_test_dao(flask_app)
    _, _, workflow_id = dao.insert_into_workflow_table(
        "Component CSRF Workflow",
        "Workflow for component csrf validation",
        "Operations",
        "Primary",
        "tester",
    )
    _, _, interaction_id = dao.insert_into_interaction_table(workflow_id, "Component CSRF Interaction", "tester")
    dao.close()

    _login(client)
    _set_context(client, workflow_id)
    response = client.post(
        "/dashboard/interaction-components/save",
        data={
            "interaction_component_name": "Rejected Component",
            "interaction_component_description": "Should not be created",
            "interaction_component_type": "Notification",
            "interaction_component_subtype": "Email",
            "interaction_id": interaction_id,
            "direction": "outbound",
        },
        follow_redirects=True,
    )

    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "session token expired" in page.lower()

    verification_dao = _build_test_dao(flask_app)
    _, _, components = verification_dao.select_all_from_interaction_component_table()
    verification_dao.close()

    assert not [
        component for component in components if component["interaction_component_name"] == "Rejected Component"
    ]