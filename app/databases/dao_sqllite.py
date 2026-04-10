import logging
import sqlite3
from datetime import datetime
from typing import Any

import config

from .dao_base import BaseDAO


def _current_timestamp() -> str:
	"""Return a UTC timestamp string formatted for persistence."""
	return datetime.utcnow().isoformat(sep=" ", timespec="seconds")


class SQLiteDatabase(BaseDAO):
	"""SQLite-backed DAO implementation that mirrors the BaseDAO contract."""

	def __init__(self, db_path: str | None = None, dbname: str | None = None):
		"""Initialize the SQLite database path and connection state."""
		runtime_config = config.get_config()
		default_name = dbname or runtime_config.DB_NAME
		self.db_path = db_path or f"{default_name}.sqlite3"
		self.connection: sqlite3.Connection | None = None

	def connect(self) -> tuple[int, str | None, Any]:
		"""Open a SQLite connection and enable row mapping plus foreign keys."""
		try:
			self.connection = sqlite3.connect(self.db_path)
			self.connection.row_factory = sqlite3.Row
			self.connection.execute("PRAGMA foreign_keys = ON")
		except sqlite3.Error as err:
			logging.error(f"[!] Error connecting to SQLite: {err}")
			self.connection = None
			return -1, str(err), None
		return 0, None, self.connection

	def ensure_connection(self) -> tuple[int, str | None, None]:
		"""Ensure that a live SQLite connection is available before an operation runs."""
		if self.connection is None:
			connect_code, connect_error, _ = self.connect()
			if connect_code != 0:
				return -1, connect_error, None

		try:
			self.connection.execute("SELECT 1")
		except sqlite3.Error as err:
			logging.warning(f"[!] SQLite ping failed, reconnecting: {err}")
			connect_code, connect_error, _ = self.connect()
			if connect_code != 0:
				return -1, connect_error, None
		return 0, None, None

	def ping(self) -> tuple[int, str | None, None]:
		"""Check that the current SQLite connection can execute a trivial query."""
		ensure_code, ensure_error, _ = self.ensure_connection()
		if ensure_code != 0:
			return -1, ensure_error, None
		return 0, None, None

	def create_database(self) -> tuple[int, str | None, None]:
		"""Ensure the SQLite database file exists by opening a connection to it."""
		ensure_code, ensure_error, _ = self.ensure_connection()
		if ensure_code != 0:
			return -1, ensure_error, None
		return 0, None, None

	def create_table(self, table_name: str, columns: dict[str, str]) -> tuple[int, str | None, None]:
		"""Create a SQLite table from a name and column-definition mapping."""
		ensure_code, ensure_error, _ = self.ensure_connection()
		if ensure_code != 0:
			return -1, ensure_error, None

		columns_sql = ", ".join(f"{column} {definition}" for column, definition in columns.items())
		statement = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
		try:
			self.connection.execute(statement)
			self.connection.commit()
		except sqlite3.Error as err:
			logging.error(f"[!] Error creating table '{table_name}': {err}")
			return -1, str(err), None
		return 0, None, None

	def show_table_ddl(self, table_name: str, filename: str | None) -> tuple[int, str | None, list]:
		"""Fetch table DDL from sqlite_master and optionally write it to disk."""
		ensure_code, ensure_error, _ = self.ensure_connection()
		if ensure_code != 0:
			return -1, ensure_error, []

		try:
			cursor = self.connection.execute(
				"SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
				(table_name,),
			)
			row = cursor.fetchone()
			if row is None or row[0] is None:
				return -1, f"Table '{table_name}' not found.", []
			ddl = [table_name, row[0]]
			if filename:
				with open(filename, "w", encoding="utf-8") as file_handle:
					file_handle.write(row[0])
		except (OSError, sqlite3.Error) as err:
			logging.error(f"[!] Error reading DDL for '{table_name}': {err}")
			return -1, str(err), []
		return 0, None, ddl

	def _insert_row(self, table_name: str, data: dict[str, Any]) -> tuple[int, str | None, Any]:
		"""Insert a row into a table using the provided column-value mapping."""
		ensure_code, ensure_error, _ = self.ensure_connection()
		if ensure_code != 0:
			return -1, ensure_error, None

		columns = ", ".join(data.keys())
		placeholders = ", ".join("?" for _ in data)
		statement = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
		try:
			cursor = self.connection.execute(statement, tuple(data.values()))
			self.connection.commit()
			return 0, None, cursor.lastrowid
		except sqlite3.Error as err:
			logging.error(f"[!] Error inserting into '{table_name}': {err}")
			return -1, str(err), None

	def _update_row(
		self,
		table_name: str,
		key_column: str,
		key_value: Any,
		data: dict[str, Any],
	) -> tuple[int, str | None, Any]:
		"""Update a single row identified by a key column and key value."""
		ensure_code, ensure_error, _ = self.ensure_connection()
		if ensure_code != 0:
			return -1, ensure_error, None

		assignments = ", ".join(f"{column} = ?" for column in data)
		statement = f"UPDATE {table_name} SET {assignments} WHERE {key_column} = ?"
		try:
			cursor = self.connection.execute(statement, tuple(data.values()) + (key_value,))
			self.connection.commit()
			if cursor.rowcount == 0:
				return -1, f"No row found for {key_column}={key_value}.", None
		except sqlite3.Error as err:
			logging.error(f"[!] Error updating '{table_name}': {err}")
			return -1, str(err), None
		return 0, None, key_value

	def _delete_row(self, table_name: str, key_column: str, key_value: Any) -> tuple[int, str | None, None]:
		"""Delete a single row identified by a key column and key value."""
		ensure_code, ensure_error, _ = self.ensure_connection()
		if ensure_code != 0:
			return -1, ensure_error, None

		try:
			cursor = self.connection.execute(
				f"DELETE FROM {table_name} WHERE {key_column} = ?",
				(key_value,),
			)
			self.connection.commit()
			if cursor.rowcount == 0:
				return -1, f"No row found for {key_column}={key_value}.", None
		except sqlite3.Error as err:
			logging.error(f"[!] Error deleting from '{table_name}': {err}")
			return -1, str(err), None
		return 0, None, None

	def _select_row(self, table_name: str, key_column: str, key_value: Any) -> tuple[int, str | None, dict]:
		"""Fetch a single row as a dictionary using a key column and value."""
		ensure_code, ensure_error, _ = self.ensure_connection()
		if ensure_code != 0:
			return -1, ensure_error, {}

		try:
			cursor = self.connection.execute(
				f"SELECT * FROM {table_name} WHERE {key_column} = ?",
				(key_value,),
			)
			row = cursor.fetchone()
		except sqlite3.Error as err:
			logging.error(f"[!] Error selecting from '{table_name}': {err}")
			return -1, str(err), {}

		if row is None:
			return -1, f"No row found for {key_column}={key_value}.", {}
		return 0, None, dict(row)

	def _select_all_rows(self, table_name: str) -> tuple[int, str | None, list]:
		"""Fetch all rows from a table and return them as dictionaries."""
		ensure_code, ensure_error, _ = self.ensure_connection()
		if ensure_code != 0:
			return -1, ensure_error, []

		try:
			cursor = self.connection.execute(f"SELECT * FROM {table_name}")
			rows = [dict(row) for row in cursor.fetchall()]
		except sqlite3.Error as err:
			logging.error(f"[!] Error selecting all from '{table_name}': {err}")
			return -1, str(err), []
		return 0, None, rows

	def _delete_all_rows(self, table_name: str) -> tuple[int, str | None, None]:
		"""Delete every row from the specified table."""
		ensure_code, ensure_error, _ = self.ensure_connection()
		if ensure_code != 0:
			return -1, ensure_error, None

		try:
			self.connection.execute(f"DELETE FROM {table_name}")
			self.connection.commit()
		except sqlite3.Error as err:
			logging.error(f"[!] Error deleting all rows from '{table_name}': {err}")
			return -1, str(err), None
		return 0, None, None

	def create_workflow_table(self) -> tuple[int, str | None, None]:
		"""Create the workflows table in the SQLite database."""
		columns = {
			"workflow_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
			"workflow_name": "TEXT NOT NULL",
			"workflow_description": "TEXT",
			"workflow_type": "TEXT NOT NULL",
			"workflow_subtype": "TEXT",
			"created_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
			"updated_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
			"created_by": "TEXT",
			"updated_by": "TEXT",
		}
		return self.create_table("workflows", columns)

	def show_workflow_table_ddl(self, filename: str | None) -> tuple[int, str | None, list]:
		"""Return the DDL for the workflows table."""
		return self.show_table_ddl("workflows", filename)

	def drop_workflow_table(self) -> tuple[int, str | None, None]:
		"""Drop the workflows table if it exists."""
		return self._drop_table("workflows")

	def insert_into_workflow_table(
		self,
		workflow_name: str,
		workflow_description: str,
		workflow_type: str,
		workflow_subtype: str,
		created_by: str,
	) -> tuple[int, str | None, Any]:
		"""Insert a workflow row and return the inserted identifier."""
		return self._insert_row(
			"workflows",
			{
				"workflow_name": workflow_name,
				"workflow_description": workflow_description,
				"workflow_type": workflow_type,
				"workflow_subtype": workflow_subtype,
				"created_by": created_by,
			},
		)

	def update_workflow_table(
		self,
		workflow_id: int,
		workflow_name: str,
		workflow_description: str,
		workflow_type: str,
		workflow_subtype: str,
		updated_by: str,
	) -> tuple[int, str | None, Any]:
		"""Update a workflow row identified by workflow_id."""
		return self._update_row(
			"workflows",
			"workflow_id",
			workflow_id,
			{
				"workflow_name": workflow_name,
				"workflow_description": workflow_description,
				"workflow_type": workflow_type,
				"workflow_subtype": workflow_subtype,
				"updated_by": updated_by,
				"updated_at": _current_timestamp(),
			},
		)

	def delete_from_workflow_table(self, workflow_id: int) -> tuple[int, str | None, None]:
		"""Delete a workflow row by identifier."""
		return self._delete_row("workflows", "workflow_id", workflow_id)

	def select_from_workflow_table(self, workflow_id: int) -> tuple[int, str | None, dict]:
		"""Fetch a single workflow row by identifier."""
		return self._select_row("workflows", "workflow_id", workflow_id)

	def select_all_from_workflow_table(self) -> tuple[int, str | None, list]:
		"""Fetch all workflow rows."""
		return self._select_all_rows("workflows")

	def delete_all_from_workflow_table(self) -> tuple[int, str | None, None]:
		"""Delete all workflow rows."""
		return self._delete_all_rows("workflows")

	def create_role_table(self) -> tuple[int, str | None, None]:
		"""Create the roles table after ensuring the workflows table exists."""
		workflow_code, workflow_error, _ = self.create_workflow_table()
		if workflow_code != 0:
			return -1, workflow_error, None

		columns = {
			"role_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
			"workspace_id": "INTEGER NOT NULL",
			"role_name": "TEXT NOT NULL",
			"role_description": "TEXT",
			"role_type": "TEXT NOT NULL",
			"role_subtype": "TEXT",
			"created_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
			"updated_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
			"created_by": "TEXT",
			"updated_by": "TEXT",
			"FOREIGN KEY (workspace_id) REFERENCES workflows(workflow_id) ON UPDATE CASCADE ON DELETE CASCADE": "",
		}
		return self.create_table("roles", columns)

	def show_role_table_ddl(self, filename: str | None) -> tuple[int, str | None, list]:
		"""Return the DDL for the roles table."""
		return self.show_table_ddl("roles", filename)

	def drop_role_table(self) -> tuple[int, str | None, None]:
		"""Drop the roles table if it exists."""
		return self._drop_table("roles")

	def insert_into_role_table(
		self,
		workspace_id: int,
		role_name: str,
		role_description: str,
		role_type: str,
		role_subtype: str,
		created_by: str,
	) -> tuple[int, str | None, Any]:
		"""Insert a role row and return the inserted identifier."""
		return self._insert_row(
			"roles",
			{
				"workspace_id": workspace_id,
				"role_name": role_name,
				"role_description": role_description,
				"role_type": role_type,
				"role_subtype": role_subtype,
				"created_by": created_by,
			},
		)

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
		"""Update a role row identified by role_id."""
		return self._update_row(
			"roles",
			"role_id",
			role_id,
			{
				"workspace_id": workspace_id,
				"role_name": role_name,
				"role_description": role_description,
				"role_type": role_type,
				"role_subtype": role_subtype,
				"updated_by": updated_by,
				"updated_at": _current_timestamp(),
			},
		)

	def delete_from_role_table(self, role_id: int) -> tuple[int, str | None, None]:
		"""Delete a role row by identifier."""
		return self._delete_row("roles", "role_id", role_id)

	def select_from_role_table(self, role_id: int) -> tuple[int, str | None, dict]:
		"""Fetch a single role row by identifier."""
		return self._select_row("roles", "role_id", role_id)

	def select_all_from_role_table(self) -> tuple[int, str | None, list]:
		"""Fetch all role rows."""
		return self._select_all_rows("roles")

	def delete_all_from_role_table(self) -> tuple[int, str | None, None]:
		"""Delete all role rows."""
		return self._delete_all_rows("roles")

	def create_guard_table(self) -> tuple[int, str | None, None]:
		"""Create the guards table after ensuring the workflows table exists."""
		workflow_code, workflow_error, _ = self.create_workflow_table()
		if workflow_code != 0:
			return -1, workflow_error, None

		columns = {
			"guard_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
			"workspace_id": "INTEGER NOT NULL",
			"guard_name": "TEXT NOT NULL",
			"guard_description": "TEXT",
			"guard_type": "TEXT NOT NULL",
			"guard_subtype": "TEXT",
			"created_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
			"updated_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
			"created_by": "TEXT",
			"updated_by": "TEXT",
			"FOREIGN KEY (workspace_id) REFERENCES workflows(workflow_id) ON UPDATE CASCADE ON DELETE CASCADE": "",
		}
		return self.create_table("guards", columns)

	def show_guard_table_ddl(self, filename: str | None) -> tuple[int, str | None, list]:
		"""Return the DDL for the guards table."""
		return self.show_table_ddl("guards", filename)

	def drop_guard_table(self) -> tuple[int, str | None, None]:
		"""Drop the guards table if it exists."""
		return self._drop_table("guards")

	def insert_into_guard_table(
		self,
		workspace_id: int,
		guard_name: str,
		guard_description: str,
		guard_type: str,
		guard_subtype: str,
		created_by: str,
	) -> tuple[int, str | None, Any]:
		"""Insert a guard row and return the inserted identifier."""
		return self._insert_row(
			"guards",
			{
				"workspace_id": workspace_id,
				"guard_name": guard_name,
				"guard_description": guard_description,
				"guard_type": guard_type,
				"guard_subtype": guard_subtype,
				"created_by": created_by,
			},
		)

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
		"""Update a guard row identified by guard_id."""
		return self._update_row(
			"guards",
			"guard_id",
			guard_id,
			{
				"workspace_id": workspace_id,
				"guard_name": guard_name,
				"guard_description": guard_description,
				"guard_type": guard_type,
				"guard_subtype": guard_subtype,
				"updated_by": updated_by,
				"updated_at": _current_timestamp(),
			},
		)

	def delete_from_guard_table(self, guard_id: int) -> tuple[int, str | None, None]:
		"""Delete a guard row by identifier."""
		return self._delete_row("guards", "guard_id", guard_id)

	def select_from_guard_table(self, guard_id: int) -> tuple[int, str | None, dict]:
		"""Fetch a single guard row by identifier."""
		return self._select_row("guards", "guard_id", guard_id)

	def select_all_from_guard_table(self) -> tuple[int, str | None, list]:
		"""Fetch all guard rows."""
		return self._select_all_rows("guards")

	def delete_all_from_guard_table(self) -> tuple[int, str | None, None]:
		"""Delete all guard rows."""
		return self._delete_all_rows("guards")

	def create_interaction_table(self) -> tuple[int, str | None, None]:
		"""Create the interactions table after ensuring the workflows table exists."""
		workflow_code, workflow_error, _ = self.create_workflow_table()
		if workflow_code != 0:
			return -1, workflow_error, None

		columns = {
			"interaction_id": "INTEGER PRIMARY KEY",
			"workflow_id": "INTEGER NOT NULL",
			"interaction_name": "TEXT NOT NULL",
			"created_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
			"updated_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
			"created_by": "TEXT",
			"updated_by": "TEXT",
			"FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id) ON UPDATE CASCADE ON DELETE CASCADE": "",
		}
		return self.create_table("interaction_components", columns)

	def show_interaction_table_ddl(self, filename: str | None) -> tuple[int, str | None, list]:
		"""Return the DDL for the interactions table."""
		return self.show_table_ddl("interaction_components", filename)

	def drop_interaction_table(self) -> tuple[int, str | None, None]:
		"""Drop the interactions table if it exists."""
		return self._drop_table("interaction_components")

	def insert_into_interaction_table(
		self,
		interaction_id: int,
		workflow_id: int,
		interaction_name: str,
		created_by: str,
	) -> tuple[int, str | None, Any]:
		"""Insert an interaction row and return the inserted identifier."""
		return self._insert_row(
			"interaction_components",
			{
				"interaction_id": interaction_id,
				"workflow_id": workflow_id,
				"interaction_name": interaction_name,
				"created_by": created_by,
			},
		)

	def update_interaction_table(
		self,
		interaction_id: int,
		workflow_id: int,
		interaction_name: str,
		updated_by: str,
	) -> tuple[int, str | None, Any]:
		"""Update an interaction row identified by interaction_id."""
		return self._update_row(
			"interaction_components",
			"interaction_id",
			interaction_id,
			{
				"workflow_id": workflow_id,
				"interaction_name": interaction_name,
				"updated_by": updated_by,
				"updated_at": _current_timestamp(),
			},
		)

	def delete_from_interaction_table(self, interaction_id: int) -> tuple[int, str | None, None]:
		"""Delete an interaction row by identifier."""
		return self._delete_row("interaction_components", "interaction_id", interaction_id)

	def select_from_interaction_table(self, interaction_id: int) -> tuple[int, str | None, dict]:
		"""Fetch a single interaction row by identifier."""
		return self._select_row("interaction_components", "interaction_id", interaction_id)

	def select_all_from_interaction_table(self) -> tuple[int, str | None, list]:
		"""Fetch all interaction rows."""
		return self._select_all_rows("interaction_components")

	def delete_all_from_interaction_table(self) -> tuple[int, str | None, None]:
		"""Delete all interaction rows."""
		return self._delete_all_rows("interaction_components")

	def create_interaction_component_table(self) -> tuple[int, str | None, None]:
		"""Create the interaction component table after creating all prerequisite tables."""
		for builder in (
			self.create_workflow_table,
			self.create_role_table,
			self.create_guard_table,
			self.create_interaction_table,
		):
			build_code, build_error, _ = builder()
			if build_code != 0:
				return -1, build_error, None

		columns = {
			"interaction_component_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
			"workflow_id": "INTEGER NOT NULL",
			"interaction_component_name": "TEXT NOT NULL",
			"interaction_component_description": "TEXT",
			"interaction_component_type": "TEXT NOT NULL",
			"interaction_component_subtype": "TEXT",
			"interaction_id": "INTEGER NOT NULL",
			"guard_id": "INTEGER",
			"role_id": "INTEGER",
			"direction": "TEXT NOT NULL",
			"created_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
			"updated_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
			"created_by": "TEXT",
			"updated_by": "TEXT",
			"FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id) ON UPDATE CASCADE ON DELETE CASCADE": "",
			"FOREIGN KEY (interaction_id) REFERENCES interaction_components(interaction_id) ON UPDATE CASCADE ON DELETE CASCADE": "",
			"FOREIGN KEY (guard_id) REFERENCES guards(guard_id) ON UPDATE CASCADE ON DELETE SET NULL": "",
			"FOREIGN KEY (role_id) REFERENCES roles(role_id) ON UPDATE CASCADE ON DELETE SET NULL": "",
		}
		return self.create_table("interaction_component", columns)

	def show_interaction_component_table_ddl(self, filename: str | None) -> tuple[int, str | None, list]:
		"""Return the DDL for the interaction component table."""
		return self.show_table_ddl("interaction_component", filename)

	def drop_interaction_component_table(self) -> tuple[int, str | None, None]:
		"""Drop the interaction component table if it exists."""
		return self._drop_table("interaction_component")

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
		"""Insert an interaction component row and return the inserted identifier."""
		workflow_id = self._workflow_id_for_interaction(interaction_id)
		if workflow_id is None:
			return -1, f"No interaction found for interaction_id={interaction_id}.", None
		return self._insert_row(
			"interaction_component",
			{
				"workflow_id": workflow_id,
				"interaction_component_name": interaction_component_name,
				"interaction_component_description": interaction_component_description,
				"interaction_component_type": interaction_component_type,
				"interaction_component_subtype": interaction_component_subtype,
				"interaction_id": interaction_id,
				"guard_id": guard_id,
				"role_id": role_id,
				"direction": direction,
				"created_by": created_by,
			},
		)

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
		"""Update an interaction component row identified by interaction_component_id."""
		workflow_id = self._workflow_id_for_interaction(interaction_id)
		if workflow_id is None:
			return -1, f"No interaction found for interaction_id={interaction_id}.", None
		return self._update_row(
			"interaction_component",
			"interaction_component_id",
			interaction_component_id,
			{
				"workflow_id": workflow_id,
				"interaction_component_name": interaction_component_name,
				"interaction_component_description": interaction_component_description,
				"interaction_component_type": interaction_component_type,
				"interaction_component_subtype": interaction_component_subtype,
				"interaction_id": interaction_id,
				"guard_id": guard_id,
				"role_id": role_id,
				"direction": direction,
				"updated_by": updated_by,
				"updated_at": _current_timestamp(),
			},
		)

	def delete_from_interaction_component_table(self, interaction_component_id: int) -> tuple[int, str | None, None]:
		"""Delete an interaction component row by identifier."""
		return self._delete_row("interaction_component", "interaction_component_id", interaction_component_id)

	def select_from_interaction_component_table(self, interaction_component_id: int) -> tuple[int, str | None, dict]:
		"""Fetch a single interaction component row by identifier."""
		return self._select_row("interaction_component", "interaction_component_id", interaction_component_id)

	def select_all_from_interaction_component_table(self) -> tuple[int, str | None, list]:
		"""Fetch all interaction component rows."""
		return self._select_all_rows("interaction_component")

	def delete_all_from_interaction_component_table(self) -> tuple[int, str | None, None]:
		"""Delete all interaction component rows."""
		return self._delete_all_rows("interaction_component")

	def close(self) -> None:
		"""Close the active SQLite connection and clear the cached handle."""
		if self.connection is not None:
			self.connection.close()
			self.connection = None

	def _drop_table(self, table_name: str) -> tuple[int, str | None, None]:
		"""Drop a table if it exists."""
		ensure_code, ensure_error, _ = self.ensure_connection()
		if ensure_code != 0:
			return -1, ensure_error, None

		try:
			self.connection.execute(f"DROP TABLE IF EXISTS {table_name}")
			self.connection.commit()
		except sqlite3.Error as err:
			logging.error(f"[!] Error dropping table '{table_name}': {err}")
			return -1, str(err), None
		return 0, None, None

	def _workflow_id_for_interaction(self, interaction_id: int) -> int | None:
		"""Look up the workflow_id associated with a stored interaction row."""
		ensure_code, _, _ = self.ensure_connection()
		if ensure_code != 0:
			return None
		try:
			cursor = self.connection.execute(
				"SELECT workflow_id FROM interaction_components WHERE interaction_id = ?",
				(interaction_id,),
			)
			row = cursor.fetchone()
		except sqlite3.Error:
			return None
		if row is None:
			return None
		return int(row[0])
