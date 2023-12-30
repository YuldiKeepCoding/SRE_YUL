"""
Module for define API endpoints
"""

from typing import Optional
import logging
from fastapi import FastAPI, Body, status
from fastapi.responses import JSONResponse
from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperCornConfig
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator
from bson import ObjectId
from typing_extensions import Annotated
from prometheus_client import Counter

app = FastAPI()

REQUESTS = Counter('server_requests_total', 'Total number of requests to this webserver')
HEALTHCHECK_REQUESTS = Counter('healthcheck_requests_total',
    'Total number of requests to healthcheck')
MAIN_ENDPOINT_REQUESTS = Counter('main_requests_total',
    'Total number of requests to main endpoint')
STUDENT_CREATE_REQUESTS = Counter('students_create_total',
    'Total number of requests to the endpoint for create a student')


# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]

class StudentModel(BaseModel):
    """
    Container for a single student record.
    """

    # The primary key for the StudentModel, stored as a `str` on the instance.
    # This will be aliased to `_id` when sent to MongoDB,
    # but provided as `id` in the API requests and responses.
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(...)
    email: EmailStr = Field(...)
    course: str = Field(...)
    gpa: float = Field(..., le=4.0)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "course": "Experiments, Science, and Fashion in Nanophotonics",
                "gpa": 3.0,
            }
        },
    )

class UpdateStudentModel(BaseModel):
    """
    UpdateStudentModel define attributes of students used for update
    """
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    course: Optional[str] = None
    gpa: Optional[float] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "course": "Experiments, Science, and Fashion in Nanophotonics",
                "gpa": 3.0,
            }
        },
    )

app = FastAPI()

class StudentsServer:
    """
    StudentsServer class define fastapi configuration using StudentsAction to access
    internal API
    """
    _hypercorn_config = None

    def __init__(self, config, db_handler):
        self._hypercorn_config = HyperCornConfig()
        self._config = config
        self._logger = self.__get_logger()
        self._db_handler = db_handler

    def __get_logger(self):
        logger = logging.getLogger(self._config.LOG_CONFIG['name'])
        logger.setLevel(self._config.LOG_CONFIG['level'])
        log_handler = self._config.LOG_CONFIG['stream_handler']
        log_formatter = logging.Formatter(
            fmt=self._config.LOG_CONFIG['format'],
            datefmt=self._config.LOG_CONFIG['date_fmt']
        )
        log_handler.setFormatter(log_formatter)
        logger.addHandler(log_handler)
        return logger

    async def run_server(self):
        """Starts the server with the config parameters"""

        self._hypercorn_config.bind = [f'0.0.0.0:{self._config.FASTAPI_CONFIG["port"]}']
        self._hypercorn_config.keep_alive_timeout = 90
        self.add_routes()
        await serve(app, self._hypercorn_config)

    def add_routes(self):
        """Maps the endpoint routes with their methods."""

        app.add_api_route(
            path="/health",
            endpoint=self.health_check,
            summary="Health endpoint",
            methods=["GET"],
            status_code=status.HTTP_200_OK,
        )

        app.add_api_route(
            path="/api/student",
            endpoint=self.create_student,
            summary="Add a new student",
            methods=["POST"],
            response_model=StudentModel,
            response_description="Create a new student",
            response_model_by_alias=False,
        )

        app.add_api_route(
            path="/hello",
            endpoint=self.read_main,
            methods=["GET"]
        )

    async def read_main(self):
        """Simple main endpoint"""
        self._logger.info("Main endpoint called")

        # Increment counter used for register the total number of calls in the webserver
        REQUESTS.inc()
        # Increment counter used for register the requests to main endpoint
        MAIN_ENDPOINT_REQUESTS.inc()

        return JSONResponse(status_code=status.HTTP_200_OK, content={"msg": "Hello World"})

    async def health_check(self):
        """Simple health check."""

        self._logger.info("Healthcheck endpoint called")

        # Increment counter used for register the total number of calls in the webserver
        REQUESTS.inc()
        # Increment counter used for register the requests to healtcheck endpoint
        HEALTHCHECK_REQUESTS.inc()

        return JSONResponse(status_code=status.HTTP_200_OK, content={"health": "ok"})

    async def create_student(self, student: StudentModel = Body(...)):
        """Add a new student
        Parameters
        ----------
        student
          Student representation
        Returns
        -------
        Response from the action layer
        """
        # Increment counter used for register the requests to create student endpoint
        STUDENT_CREATE_REQUESTS.inc()
        # Increment counter used for register the total number of calls in the webserver
        REQUESTS.inc()

        self._logger.debug('Trying to add student %s', student)
        new_student = await self._db_handler[self._config.MONGODB_COLLECTION].insert_one(
            student.model_dump(by_alias=True, exclude=["id"])
        )
        created_student = await self._db_handler[self._config.MONGODB_COLLECTION].\
            find_one({"_id": new_student.inserted_id})

        self._logger.debug('Added student successfully with _id %s', new_student.inserted_id)
        created_student['_id'] = str(created_student['_id'])
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_student)
