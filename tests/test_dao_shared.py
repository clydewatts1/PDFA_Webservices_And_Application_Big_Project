import pytest
import os
from app.databases.dao_mysql import MySQLDatabase
from app.databases.dao_sqllite import SQLiteDatabase

# 1. Define fixtures for each database backend
@pytest.fixture
def mysql_dao():
    """Setup and teardown for MySQL."""
    # Use environment variables or test-specific config
    dao = MySQLDatabase(password='root',dbname="test_db")
    dao.connect()
    dao.drop_workflow_table()
    dao.create_workflow_table()
    yield dao
    # Teardown: Clean up the test database
    dao.drop_workflow_table()
    dao.close()

@pytest.fixture
def sqlite_dao(tmp_path):
    """Setup and teardown for SQLite using a temporary file."""
    db_file = tmp_path / "test_workflows.db"
    dao = SQLiteDatabase(db_path=str(db_file))
    dao.connect()
    dao.create_workflow_table()
    yield dao
    # Teardown
    dao.close()

# 2. Use parametrization to run the same tests on both DAOs
@pytest.mark.parametrize("dao_fixture", ["mysql_dao", "sqlite_dao"])
def test_workflow_crud_lifecycle(dao_fixture, request):
    """
    Test the full CRUD lifecycle for a workflow.
    This test runs twice: once for MySQL and once for SQLite.
    """
    # Dynamically get the DAO instance from the fixture name
    dao = request.getfixturevalue(dao_fixture)

    # --- TEST INSERT ---
    name = "Test Workflow"
    desc = "A workflow for testing shared logic"
    w_type = "CI/CD"
    w_subtype = "shared-test"
    user = "tester"

    code, err, workflow_id = dao.insert_into_workflow_table(
        name, desc, w_type, w_subtype, user
    )
    
    assert code == 0, f"Insert failed: {err}"
    assert workflow_id is not None

    # --- TEST SELECT (Single) ---
    code, err, data = dao.select_from_workflow_table(workflow_id)
    assert code == 0
    assert data["workflow_name"] == name
    assert data["created_by"] == user

    # --- TEST UPDATE ---
    new_name = "Updated Workflow Name"
    code, err, updated_id = dao.update_workflow_table(
        workflow_id, new_name, desc, w_type, w_subtype, "updater"
    )
    assert code == 0
    
    # Verify update
    _, _, updated_data = dao.select_from_workflow_table(workflow_id)
    assert updated_data["workflow_name"] == new_name

    # --- TEST SELECT ALL ---
    code, err, all_rows = dao.select_all_from_workflow_table()
    assert code == 0
    assert len(all_rows) >= 1

    # --- TEST DELETE ---
    code, err, _ = dao.delete_from_workflow_table(workflow_id)
    assert code == 0
    
    # Verify deletion
    code, err, data = dao.select_from_workflow_table(workflow_id)
    assert code == -1 # Should fail to find the row

# 2. Use parametrization to run the same tests on both DAOs
@pytest.mark.parametrize("dao_fixture", ["mysql_dao", "sqlite_dao"])
def test_workflow_duplicate_insert(dao_fixture, request):
    """
    Test that inserting a duplicate workflow name fails.
    This test runs twice: once for MySQL and once for SQLite.
    """
    dao = request.getfixturevalue(dao_fixture)

    name = "Duplicate Workflow"
    desc = "Testing duplicate insert"
    w_type = "CI/CD"
    w_subtype = "duplicate-test"
    user = "tester"

    # First insert should succeed
    code, err, workflow_id = dao.insert_into_workflow_table(
        name, desc, w_type, w_subtype, user
    )
    assert code == 0

    # Second insert with the same name should fail (assuming unique constraint)
    code, err, _ = dao.insert_into_workflow_table(
        name, desc, w_type, w_subtype, user
    )
    assert code != 0, "Duplicate insert should have failed"