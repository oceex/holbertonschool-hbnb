#!/usr/bin/python3
"""Tests for the standalone SQL scripts in sql/."""

import re
import sqlite3
import tempfile
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace

from app.models.user import User


PART3_DIR = Path(__file__).resolve().parents[1]
SQL_DIR = PART3_DIR / "sql"
SCHEMA_SQL = SQL_DIR / "schema.sql"
SEED_SQL = SQL_DIR / "seed.sql"
CRUD_SQL = SQL_DIR / "crud_test.sql"

ADMIN_ID = "36c9050e-ddd3-4c3b-9731-9f487208bbc1"
ADMIN_EMAIL = "admin@hbnb.io"
ADMIN_PASSWORD = "admin1234"
AMENITY_NAMES = {"WiFi", "Swimming Pool", "Air Conditioning"}

TEST_PLACE_ID = "55555555-5555-4555-8555-555555555555"
TEST_REVIEW_ID = "66666666-6666-4666-8666-666666666666"
UNKNOWN_USER_ID = "77777777-7777-4777-8777-777777777777"
UNKNOWN_PLACE_ID = "88888888-8888-4888-8888-888888888888"
UNKNOWN_AMENITY_ID = "99999999-9999-4999-8999-999999999999"


class SQLScriptTestCase(unittest.TestCase):
    """Create an isolated SQLite database for every test."""

    def setUp(self):
        """Open a temporary database and execute the raw schema."""
        self.temporary_directory = tempfile.TemporaryDirectory()
        database_path = Path(self.temporary_directory.name) / "task9.db"
        self.connection = sqlite3.connect(database_path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.execute_script(SCHEMA_SQL)

    def tearDown(self):
        """Close and remove the isolated database."""
        self.connection.close()
        self.temporary_directory.cleanup()

    def execute_script(self, path):
        """Execute one raw SQL file without invoking SQLAlchemy."""
        sql = path.read_text(encoding="utf-8")
        self.connection.executescript(sql)

    def seed_database(self):
        """Load the required administrator and Amenities."""
        self.execute_script(SEED_SQL)

    def table_info(self, table):
        """Return SQLite column metadata keyed by column name."""
        rows = self.connection.execute(
            f"PRAGMA table_info({table})"
        ).fetchall()
        return {row[1]: row for row in rows}

    def unique_column_sets(self, table):
        """Return every unique or primary-key index as a column tuple."""
        column_sets = set()
        indexes = self.connection.execute(
            f"PRAGMA index_list({table})"
        ).fetchall()
        for index in indexes:
            if not index[2]:
                continue
            columns = self.connection.execute(
                f"PRAGMA index_info({index[1]})"
            ).fetchall()
            column_sets.add(tuple(column[2] for column in columns))
        return column_sets

    def foreign_keys(self, table):
        """Return child-column, table, and parent-column FK triples."""
        rows = self.connection.execute(
            f"PRAGMA foreign_key_list({table})"
        ).fetchall()
        return {(row[3], row[2], row[4]) for row in rows}

    def assert_integrity_error(self, statement, parameters=()):
        """Assert one statement fails without affecting later assertions."""
        self.connection.execute("SAVEPOINT expected_integrity_error")
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                self.connection.execute(statement, parameters)
        finally:
            self.connection.execute(
                "ROLLBACK TO SAVEPOINT expected_integrity_error"
            )
            self.connection.execute(
                "RELEASE SAVEPOINT expected_integrity_error"
            )

    def insert_place(self, place_id=TEST_PLACE_ID, owner_id=ADMIN_ID):
        """Insert a Place fixture using direct SQL."""
        self.connection.execute(
            """
            INSERT INTO places (
                id, title, description, price, latitude, longitude, owner_id,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?,
                      CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
            (
                place_id,
                "Integrity Test Place",
                "Created by a raw SQL test.",
                100.00,
                24.7136,
                46.6753,
                owner_id,
            ),
        )


class TestSQLSchema(SQLScriptTestCase):
    """Verify the Task 9 tables and declared constraints."""

    EXPECTED_COLUMNS = {
        "users": {
            "id": "CHAR(36)",
            "first_name": "VARCHAR(50)",
            "last_name": "VARCHAR(50)",
            "email": "VARCHAR(120)",
            "password": "VARCHAR(128)",
            "is_admin": "BOOLEAN",
            "created_at": "DATETIME",
            "updated_at": "DATETIME",
        },
        "places": {
            "id": "CHAR(36)",
            "title": "VARCHAR(100)",
            "description": "VARCHAR(1000)",
            "price": "DECIMAL(10, 2)",
            "latitude": "FLOAT",
            "longitude": "FLOAT",
            "image_url": "VARCHAR(500)",
            "location": "VARCHAR(150)",
            "owner_id": "CHAR(36)",
            "created_at": "DATETIME",
            "updated_at": "DATETIME",
        },
        "reviews": {
            "id": "CHAR(36)",
            "text": "VARCHAR(1000)",
            "rating": "INT",
            "user_id": "CHAR(36)",
            "place_id": "CHAR(36)",
            "created_at": "DATETIME",
            "updated_at": "DATETIME",
        },
        "amenities": {
            "id": "CHAR(36)",
            "name": "VARCHAR(50)",
            "description": "VARCHAR(1000)",
            "created_at": "DATETIME",
            "updated_at": "DATETIME",
        },
        "place_amenity": {
            "place_id": "CHAR(36)",
            "amenity_id": "CHAR(36)",
        },
    }

    def test_schema_columns_match_the_mapped_models(self):
        """Verify the raw schema and the ORM describe the same columns.

        Without this the two definitions drift apart silently, and a database
        built from schema.sql then fails at runtime on a missing column.
        """
        from app import db
        from tests import app

        with app.app_context():
            orm_columns = {
                table.name: {column.name for column in table.columns}
                for table in db.metadata.sorted_tables
            }

        for table, columns in orm_columns.items():
            with self.subTest(table=table):
                self.assertEqual(set(self.table_info(table)), columns)

    def test_required_tables_and_declared_column_types(self):
        """Verify all required tables, columns, and SQL types."""
        tables = {
            row[0]
            for row in self.connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        self.assertEqual(tables, set(self.EXPECTED_COLUMNS))

        for table, expected_columns in self.EXPECTED_COLUMNS.items():
            with self.subTest(table=table):
                actual = self.table_info(table)
                self.assertEqual(set(actual), set(expected_columns))
                self.assertEqual(
                    {name: row[2] for name, row in actual.items()},
                    expected_columns,
                )

    def test_primary_keys(self):
        """Verify entity and association primary keys."""
        for table in ("users", "places", "reviews", "amenities"):
            with self.subTest(table=table):
                info = self.table_info(table)
                self.assertEqual(info["id"][5], 1)

        association = self.table_info("place_amenity")
        self.assertEqual(association["place_id"][5], 1)
        self.assertEqual(association["amenity_id"][5], 2)

    def test_unique_constraints(self):
        """Verify required scalar and composite uniqueness."""
        self.assertIn(("email",), self.unique_column_sets("users"))
        self.assertIn(("name",), self.unique_column_sets("amenities"))
        self.assertIn(
            ("user_id", "place_id"),
            self.unique_column_sets("reviews"),
        )
        self.assertIn(
            ("place_id", "amenity_id"),
            self.unique_column_sets("place_amenity"),
        )

    def test_foreign_keys(self):
        """Verify every required relationship foreign key."""
        self.assertEqual(
            self.foreign_keys("places"),
            {("owner_id", "users", "id")},
        )
        self.assertEqual(
            self.foreign_keys("reviews"),
            {
                ("user_id", "users", "id"),
                ("place_id", "places", "id"),
            },
        )
        self.assertEqual(
            self.foreign_keys("place_amenity"),
            {
                ("place_id", "places", "id"),
                ("amenity_id", "amenities", "id"),
            },
        )

    def test_rating_check_and_admin_default(self):
        """Verify the rating range and administrative default."""
        schema = self.connection.execute(
            "SELECT sql FROM sqlite_master WHERE name = 'reviews'"
        ).fetchone()[0]
        self.assertRegex(
            schema,
            re.compile(
                r"CHECK\s*\(\s*rating\s+BETWEEN\s+1\s+AND\s+5\s*\)",
                re.IGNORECASE,
            ),
        )
        self.assertEqual(self.table_info("users")["is_admin"][4], "FALSE")


class TestSQLSeedData(SQLScriptTestCase):
    """Verify the fixed administrator and initial Amenities."""

    def test_required_seed_data_and_password_compatibility(self):
        """Verify seed values, UUIDs, and bcrypt compatibility."""
        self.seed_database()
        administrators = self.connection.execute(
            """
            SELECT id, first_name, last_name, email, password, is_admin
            FROM users
            WHERE id = ?
            """,
            (ADMIN_ID,),
        ).fetchall()
        self.assertEqual(len(administrators), 1)
        admin = administrators[0]
        self.assertEqual(admin[0], ADMIN_ID)
        self.assertEqual(admin[1], "Admin")
        self.assertEqual(admin[2], "HBnB")
        self.assertEqual(admin[3], ADMIN_EMAIL)
        self.assertEqual(admin[5], 1)

        stored_hash = admin[4]
        self.assertTrue(
            stored_hash != ADMIN_PASSWORD,
            "administrator password must be stored as a hash",
        )
        self.assertRegex(
            stored_hash,
            re.compile(r"^\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}$"),
        )
        password_record = SimpleNamespace(_password=stored_hash)
        self.assertTrue(User.verify_password(password_record, ADMIN_PASSWORD))
        self.assertFalse(
            User.verify_password(password_record, "incorrect-password")
        )

        amenities = self.connection.execute(
            "SELECT id, name FROM amenities"
        ).fetchall()
        self.assertEqual(len(amenities), 3)
        self.assertEqual({row[1] for row in amenities}, AMENITY_NAMES)
        amenity_ids = {row[0] for row in amenities}
        self.assertEqual(len(amenity_ids), 3)
        for amenity_id in amenity_ids:
            with self.subTest(amenity_id=amenity_id):
                parsed = uuid.UUID(amenity_id)
                self.assertEqual(parsed.version, 4)
                self.assertEqual(str(parsed), amenity_id)


class TestSQLIntegrity(SQLScriptTestCase):
    """Prove each required SQLite constraint rejects invalid data."""

    def setUp(self):
        super().setUp()
        self.seed_database()

    def test_duplicate_user_email_is_rejected(self):
        self.assert_integrity_error(
            """
            INSERT INTO users (id, first_name, last_name, email, password)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                UNKNOWN_USER_ID,
                "Duplicate",
                "Email",
                ADMIN_EMAIL,
                "$2b$12$AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            ),
        )

    def test_duplicate_amenity_name_is_rejected(self):
        self.assert_integrity_error(
            "INSERT INTO amenities (id, name) VALUES (?, ?)",
            (UNKNOWN_AMENITY_ID, "WiFi"),
        )

    def test_review_rating_below_one_is_rejected(self):
        self.insert_place()
        self.assert_integrity_error(
            """
            INSERT INTO reviews (
                id, text, rating, user_id, place_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
            (TEST_REVIEW_ID, "Too low", 0, ADMIN_ID, TEST_PLACE_ID),
        )

    def test_review_rating_above_five_is_rejected(self):
        self.insert_place()
        self.assert_integrity_error(
            """
            INSERT INTO reviews (
                id, text, rating, user_id, place_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
            (TEST_REVIEW_ID, "Too high", 6, ADMIN_ID, TEST_PLACE_ID),
        )

    def test_review_with_unknown_user_is_rejected(self):
        self.insert_place()
        self.assert_integrity_error(
            """
            INSERT INTO reviews (
                id, text, rating, user_id, place_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
            (
                TEST_REVIEW_ID,
                "Unknown user",
                4,
                UNKNOWN_USER_ID,
                TEST_PLACE_ID,
            ),
        )

    def test_review_with_unknown_place_is_rejected(self):
        self.assert_integrity_error(
            """
            INSERT INTO reviews (
                id, text, rating, user_id, place_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
            (
                TEST_REVIEW_ID,
                "Unknown place",
                4,
                ADMIN_ID,
                UNKNOWN_PLACE_ID,
            ),
        )

    def test_place_with_unknown_owner_is_rejected(self):
        self.assert_integrity_error(
            """
            INSERT INTO places (
                id, title, description, price, latitude, longitude, owner_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                TEST_PLACE_ID,
                "Unknown Owner",
                "Invalid owner relationship.",
                100.00,
                24.7136,
                46.6753,
                UNKNOWN_USER_ID,
            ),
        )

    def test_duplicate_user_place_review_is_rejected(self):
        self.insert_place()
        self.connection.execute(
            """
            INSERT INTO reviews (
                id, text, rating, user_id, place_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
            (TEST_REVIEW_ID, "First", 4, ADMIN_ID, TEST_PLACE_ID),
        )
        self.assert_integrity_error(
            """
            INSERT INTO reviews (
                id, text, rating, user_id, place_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
            (
                UNKNOWN_USER_ID,
                "Duplicate",
                5,
                ADMIN_ID,
                TEST_PLACE_ID,
            ),
        )

    def test_place_amenity_with_unknown_place_is_rejected(self):
        amenity_id = self.connection.execute(
            "SELECT id FROM amenities WHERE name = 'WiFi'"
        ).fetchone()[0]
        self.assert_integrity_error(
            "INSERT INTO place_amenity (place_id, amenity_id) VALUES (?, ?)",
            (UNKNOWN_PLACE_ID, amenity_id),
        )

    def test_place_amenity_with_unknown_amenity_is_rejected(self):
        self.insert_place()
        self.assert_integrity_error(
            "INSERT INTO place_amenity (place_id, amenity_id) VALUES (?, ?)",
            (TEST_PLACE_ID, UNKNOWN_AMENITY_ID),
        )

    def test_duplicate_place_amenity_pair_is_rejected(self):
        self.insert_place()
        amenity_id = self.connection.execute(
            "SELECT id FROM amenities WHERE name = 'WiFi'"
        ).fetchone()[0]
        self.connection.execute(
            "INSERT INTO place_amenity (place_id, amenity_id) VALUES (?, ?)",
            (TEST_PLACE_ID, amenity_id),
        )
        self.assert_integrity_error(
            "INSERT INTO place_amenity (place_id, amenity_id) VALUES (?, ?)",
            (TEST_PLACE_ID, amenity_id),
        )


class TestSQLCRUDScript(SQLScriptTestCase):
    """Execute the CRUD demonstration and verify its rollback."""

    def test_crud_script_exercises_every_table_and_rolls_back(self):
        """Verify real CRUD execution without persistent changes."""
        self.seed_database()
        tables = ("users", "amenities", "places", "reviews", "place_amenity")
        before = {
            table: self.connection.execute(
                f"SELECT * FROM {table} ORDER BY 1, 2"
            ).fetchall()
            for table in tables
        }

        operations = {
            sqlite3.SQLITE_INSERT: set(),
            sqlite3.SQLITE_READ: set(),
            sqlite3.SQLITE_UPDATE: set(),
            sqlite3.SQLITE_DELETE: set(),
        }

        def authorize(action, argument1, _argument2, _database, _trigger):
            if action in operations and argument1 in tables:
                operations[action].add(argument1)
            return sqlite3.SQLITE_OK

        self.connection.set_authorizer(authorize)
        try:
            self.execute_script(CRUD_SQL)
        finally:
            self.connection.set_authorizer(None)

        expected_tables = set(tables)
        self.assertEqual(operations[sqlite3.SQLITE_INSERT], expected_tables)
        self.assertEqual(operations[sqlite3.SQLITE_READ], expected_tables)
        self.assertEqual(operations[sqlite3.SQLITE_DELETE], expected_tables)
        self.assertEqual(
            operations[sqlite3.SQLITE_UPDATE],
            {"users", "amenities", "places", "reviews"},
        )

        after = {
            table: self.connection.execute(
                f"SELECT * FROM {table} ORDER BY 1, 2"
            ).fetchall()
            for table in tables
        }
        self.assertEqual(after, before)
        self.assertEqual(len(after["users"]), 1)
        self.assertEqual(len(after["amenities"]), 3)
        self.assertEqual(after["places"], [])
        self.assertEqual(after["reviews"], [])
        self.assertEqual(after["place_amenity"], [])


if __name__ == "__main__":
    unittest.main()
