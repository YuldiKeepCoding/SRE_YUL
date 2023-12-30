"""
Module for define e2e tests
"""

import json
import pytest
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient
from application.app import StudentsServer, StudentModel
from config import test_config as config

class TestsE2EFastApi:
    """
    Class define tests for testing StudentsClient using e2e tests with a real MongoDB
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

    @pytest.fixture
    async def setup_delete_student(self):
        """Teardown for create a student"""
        db_handler = AsyncIOMotorClient(config.MONGODB_URL)[config.MONGODB_DB]
        result = await AsyncIOMotorClient(config.MONGODB_URL).admin.command({"ping": 1})
        yield result
        mongodb = db_handler[config.MONGODB_COLLECTION]
        student = jsonable_encoder(self._valid_student_data)
        await mongodb.delete_one(student)

    @pytest.mark.asyncio
    @pytest.mark.integtest
    async def create_student_test(self, setup_delete_student):
        """Test the creation of a student"""

        db_handler = AsyncIOMotorClient(config.MONGODB_URL)[config.MONGODB_DB]
        students_server = StudentsServer(config, db_handler)

        connection = setup_delete_student

        if connection and connection.get("ok") == 1.0:
            result = await students_server.create_student(self._valid_student_data_mongo)
            result_data = json.loads(result.body.decode())

            assert result.status_code == 201
            assert result_data['name'] == self._valid_student_data["name"]
            assert result_data['email'] == self._valid_student_data["email"]
            assert result_data['course'] == self._valid_student_data["course"]
            assert result_data['gpa'] == self._valid_student_data["gpa"]
        else:
            raise Exception("Not possible connect to mongodb instance")
