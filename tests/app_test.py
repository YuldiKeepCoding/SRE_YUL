"""
Module for test API endpoints using unit tests
"""

import json
from fastapi.testclient import TestClient
from application.app import StudentsServer, StudentModel, app
from mongomock_motor import AsyncMongoMockClient
from config import test_config as config
import pytest

client = TestClient(app)

class TestFastAPIApp:
    """
    Class define tests for testing FastAPI application
    """
    _valid_student_id = "62422b3329661ce0eab2066f"
    _valid_student_name = "Jane Doe"
    _valid_student_email = "jdoe@example.com"
    _valid_student_course = "Experiments, Science, and Fashion in Nanophotonics"
    _valid_student_gpa = 3.0
    _valid_student_data = {
        "_id": f"{_valid_student_id}",
        "name": f"{_valid_student_name}",
        "email": f"{_valid_student_email}",
        "course": f"{_valid_student_course}",
        "gpa": _valid_student_gpa,
    }
    _valid_student_data_mongo = StudentModel(
        id=_valid_student_id,
        name=_valid_student_name,
        email=_valid_student_email,
        course=_valid_student_course,
        gpa=_valid_student_gpa,
    )

    @pytest.mark.asyncio
    async def read_health_test(self):
        """Test the call to the root endpoint"""
        db_handler = AsyncMongoMockClient()[config.MONGODB_DB]
        students_server = StudentsServer(config, db_handler)

        result = await students_server.health_check()
        result_data = json.loads(result.body.decode())

        assert result.status_code == 200
        assert result_data == {"health": "ok"}

    @pytest.mark.asyncio
    async def read_main_test(self):
        """Test the call to the root endpoint"""
        db_handler = AsyncMongoMockClient()[config.MONGODB_DB]
        students_server = StudentsServer(config, db_handler)

        result = await students_server.read_main()
        result_data = json.loads(result.body.decode())

        assert result.status_code == 200
        assert result_data == {"msg": "Hello World"}


    @pytest.mark.asyncio
    async def create_student_test(self):
        """Test the creation of a student"""

        db_handler = AsyncMongoMockClient()[config.MONGODB_DB]
        students_server = StudentsServer(config, db_handler)

        result = await students_server.create_student(self._valid_student_data_mongo)
        result_data = json.loads(result.body.decode('utf-8'))

        assert result.status_code == 201
        assert result_data['name'] == self._valid_student_data["name"]
        assert result_data['email'] == self._valid_student_data["email"]
        assert result_data['course'] == self._valid_student_data["course"]
        assert result_data['gpa'] == self._valid_student_data["gpa"]
