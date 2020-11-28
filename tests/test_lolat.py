#!/usr/bin/python3
"""Unit tests for lolat <> db interface."""

import pytest
from context import lolat


@pytest.mark.timeout(1)
def test_db_handle():
    """Test getting the db connection.
    Look for unhandled Errors. The mock itself tests for correct parameters."""
    lolat.db_handle()


def test_volume_map():
    """Currently nothing worth testing here"""
    pass


def test_insert_data():
    """Test inserting some data.
    Look for unhandled Errors. The mock itself tests for correct parameters."""
    db = lolat.db_handle()
    lolat.insert_data(db, -1, -1)
