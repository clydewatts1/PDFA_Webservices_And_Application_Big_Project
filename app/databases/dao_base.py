#----------------------------------------------------------------------------------------------------
#   File: dao_base.py
#   Purpose: This file defines the BaseDAO abstract class that serves as a blueprint for all DAO implementations.
#   Prompted by: Clyde W. Build bao_base.py from DAO.py, ensuring it contains only abstract method definitions and no concrete implementations.
#   Created: 2026-04-09
#----------------------------------------------------------------------------------------------------

# abstractmethod is used to declare methods that must be implemented by any subclass of BaseDAO.
# The methods are defined with the expected parameters and return types, but they do not contain any

from abc import ABC, abstractmethod
from typing import Any


class BaseDAO(ABC):
    """Abstract base class for Data Access Objects (DAOs). This class defines the interface that all DAO implementations must follow."""
    @abstractmethod
    def connect(self) -> tuple[int, str | None, Any]:
        """Open a database connection and return the status, error, and connection object."""
        pass

    @abstractmethod
    def ensure_connection(self) -> tuple[int, str | None, None]:
        """Verify that a usable database connection exists, reconnecting if needed."""
        pass

    @abstractmethod
    def ping(self) -> tuple[int, str | None, None]:
        """Check whether the current database connection is alive."""
        pass

    @abstractmethod
    def create_database(self) -> tuple[int, str | None, None]:
        """Create the backing database when the provider supports that operation."""
        pass

    @abstractmethod
    def create_table(self, table_name: str, columns: dict[str, str]) -> tuple[int, str | None, None]:
        """Create a table using the supplied name and column definitions."""
        pass

    @abstractmethod
    def show_table_ddl(self, table_name: str, filename: str | None) -> tuple[int, str | None, list]:
        """Return the DDL for a table and optionally write it to a file."""
        pass

    @abstractmethod
    def create_workflow_table(self) -> tuple[int, str | None, None]:
        """Create the workflows table."""
        pass

    @abstractmethod
    def show_workflow_table_ddl(self, filename: str | None) -> tuple[int, str | None, list]:
        """Return the DDL for the workflows table."""
        pass

    @abstractmethod
    def drop_workflow_table(self) -> tuple[int, str | None, None]:
        """Drop the workflows table."""
        pass

    @abstractmethod
    def insert_into_workflow_table(
        self,
        workflow_name: str,
        workflow_description: str,
        workflow_type: str,
        workflow_subtype: str,
        created_by: str,
    ) -> tuple[int, str | None, Any]:
        """Insert a workflow row and return the operation status and inserted identifier."""
        pass

    @abstractmethod
    def update_workflow_table(
        self,
        workflow_id: int,
        workflow_name: str,
        workflow_description: str,
        workflow_type: str,
        workflow_subtype: str,
        updated_by: str,
    ) -> tuple[int, str | None, Any]:
        """Update an existing workflow row by identifier."""
        pass

    @abstractmethod
    def delete_from_workflow_table(self, workflow_id: int) -> tuple[int, str | None, None]:
        """Delete a workflow row by identifier."""
        pass

    @abstractmethod
    def select_from_workflow_table(self, workflow_id: int) -> tuple[int, str | None, dict]:
        """Fetch a single workflow row by identifier."""
        pass

    @abstractmethod
    def select_all_from_workflow_table(self) -> tuple[int, str | None, list]:
        """Fetch all workflow rows."""
        pass

    @abstractmethod
    def delete_all_from_workflow_table(self) -> tuple[int, str | None, None]:
        """Delete all rows from the workflows table."""
        pass

    @abstractmethod
    def create_role_table(self) -> tuple[int, str | None, None]:
        """Create the roles table."""
        pass

    @abstractmethod
    def show_role_table_ddl(self, filename: str | None) -> tuple[int, str | None, list]:
        """Return the DDL for the roles table."""
        pass

    @abstractmethod
    def drop_role_table(self) -> tuple[int, str | None, None]:
        """Drop the roles table."""
        pass

    @abstractmethod
    def insert_into_role_table(
        self,
        workspace_id: int,
        role_name: str,
        role_description: str,
        role_type: str,
        role_subtype: str,
        created_by: str,
    ) -> tuple[int, str | None, Any]:
        """Insert a role row and return the operation status and inserted identifier."""
        pass

    @abstractmethod
    def update_role_table(
        self,
        role_id: int,
        workspace_id: int,
        role_name: str,
        role_description: str,
        role_type: str,
        role_subtype: str,
        updated_by: str,
    ) -> tuple[int, str | None, Any]:
        """Update an existing role row by identifier."""
        pass

    @abstractmethod
    def delete_from_role_table(self, role_id: int) -> tuple[int, str | None, None]:
        """Delete a role row by identifier."""
        pass

    @abstractmethod
    def select_from_role_table(self, role_id: int) -> tuple[int, str | None, dict]:
        """Fetch a single role row by identifier."""
        pass

    @abstractmethod
    def select_all_from_role_table(self) -> tuple[int, str | None, list]:
        """Fetch all role rows."""
        pass

    @abstractmethod
    def delete_all_from_role_table(self) -> tuple[int, str | None, None]:
        """Delete all rows from the roles table."""
        pass

    @abstractmethod
    def create_guard_table(self) -> tuple[int, str | None, None]:
        """Create the guards table."""
        pass

    @abstractmethod
    def show_guard_table_ddl(self, filename: str | None) -> tuple[int, str | None, list]:
        """Return the DDL for the guards table."""
        pass

    @abstractmethod
    def drop_guard_table(self) -> tuple[int, str | None, None]:
        """Drop the guards table."""
        pass

    @abstractmethod
    def insert_into_guard_table(
        self,
        workspace_id: int,
        guard_name: str,
        guard_description: str,
        guard_type: str,
        guard_subtype: str,
        created_by: str,
    ) -> tuple[int, str | None, Any]:
        """Insert a guard row and return the operation status and inserted identifier."""
        pass

    @abstractmethod
    def update_guard_table(
        self,
        guard_id: int,
        workspace_id: int,
        guard_name: str,
        guard_description: str,
        guard_type: str,
        guard_subtype: str,
        updated_by: str,
    ) -> tuple[int, str | None, Any]:
        """Update an existing guard row by identifier."""
        pass

    @abstractmethod
    def delete_from_guard_table(self, guard_id: int) -> tuple[int, str | None, None]:
        """Delete a guard row by identifier."""
        pass

    @abstractmethod
    def select_from_guard_table(self, guard_id: int) -> tuple[int, str | None, dict]:
        """Fetch a single guard row by identifier."""
        pass

    @abstractmethod
    def select_all_from_guard_table(self) -> tuple[int, str | None, list]:
        """Fetch all guard rows."""
        pass

    @abstractmethod
    def delete_all_from_guard_table(self) -> tuple[int, str | None, None]:
        """Delete all rows from the guards table."""
        pass

    @abstractmethod
    def create_interaction_table(self) -> tuple[int, str | None, None]:
        """Create the interactions table."""
        pass

    @abstractmethod
    def show_interaction_table_ddl(self, filename: str | None) -> tuple[int, str | None, list]:
        """Return the DDL for the interactions table."""
        pass

    @abstractmethod
    def drop_interaction_table(self) -> tuple[int, str | None, None]:
        """Drop the interactions table."""
        pass

    @abstractmethod
    def insert_into_interaction_table(
        self,
        interaction_id: int,
        workflow_id: int,
        interaction_name: str,
        created_by: str,
    ) -> tuple[int, str | None, Any]:
        """Insert an interaction row and return the operation status and inserted identifier."""
        pass

    @abstractmethod
    def update_interaction_table(
        self,
        interaction_id: int,
        workflow_id: int,
        interaction_name: str,
        updated_by: str,
    ) -> tuple[int, str | None, Any]:
        """Update an existing interaction row by identifier."""
        pass

    @abstractmethod
    def delete_from_interaction_table(self, interaction_id: int) -> tuple[int, str | None, None]:
        """Delete an interaction row by identifier."""
        pass

    @abstractmethod
    def select_from_interaction_table(self, interaction_id: int) -> tuple[int, str | None, dict]:
        """Fetch a single interaction row by identifier."""
        pass

    @abstractmethod
    def select_all_from_interaction_table(self) -> tuple[int, str | None, list]:
        """Fetch all interaction rows."""
        pass

    @abstractmethod
    def delete_all_from_interaction_table(self) -> tuple[int, str | None, None]:
        """Delete all rows from the interactions table."""
        pass

    @abstractmethod
    def create_interaction_component_table(self) -> tuple[int, str | None, None]:
        """Create the interaction components table."""
        pass

    @abstractmethod
    def show_interaction_component_table_ddl(self, filename: str | None) -> tuple[int, str | None, list]:
        """Return the DDL for the interaction components table."""
        pass

    @abstractmethod
    def drop_interaction_component_table(self) -> tuple[int, str | None, None]:
        """Drop the interaction components table."""
        pass

    @abstractmethod
    def insert_into_interaction_component_table(
        self,
        interaction_component_name: str,
        interaction_component_description: str,
        interaction_component_type: str,
        interaction_component_subtype: str,
        interaction_id: int,
        guard_id: int | None,
        role_id: int | None,
        direction: str,
        created_by: str,
    ) -> tuple[int, str | None, Any]:
        """Insert an interaction component row and return the operation status and inserted identifier."""
        pass

    @abstractmethod
    def update_interaction_component_table(
        self,
        interaction_component_id: int,
        interaction_component_name: str,
        interaction_component_description: str,
        interaction_component_type: str,
        interaction_component_subtype: str,
        interaction_id: int,
        guard_id: int | None,
        role_id: int | None,
        direction: str,
        updated_by: str,
    ) -> tuple[int, str | None, Any]:
        """Update an existing interaction component row by identifier."""
        pass

    @abstractmethod
    def delete_from_interaction_component_table(self, interaction_component_id: int) -> tuple[int, str | None, None]:
        """Delete an interaction component row by identifier."""
        pass

    @abstractmethod
    def select_from_interaction_component_table(self, interaction_component_id: int) -> tuple[int, str | None, dict]:
        """Fetch a single interaction component row by identifier."""
        pass

    @abstractmethod
    def select_all_from_interaction_component_table(self) -> tuple[int, str | None, list]:
        """Fetch all interaction component rows."""
        pass

    @abstractmethod
    def delete_all_from_interaction_component_table(self) -> tuple[int, str | None, None]:
        """Delete all rows from the interaction components table."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Release any open database resources held by the DAO."""
        pass