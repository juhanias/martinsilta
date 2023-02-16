import os

import pymongo
from pymongo.server_api import ServerApi

from src.libs.wilmapy.WilmaModels import Exam


def pushExamToDatabase(exam: Exam):
    """
    Push an exam to the database.
    :param exam: Exam to be pushed
    """
    dbconn = pymongo.MongoClient(os.getenv("MONGO"), server_api=ServerApi('1'))
    db_exam_history = dbconn["examlib"]["history"]
    db_exam_history.insert_one(
        {
            "_id": exam.date_humanreadable + exam.name + exam.course_fullname,
            "name": exam.name,
            "course": exam.course_fullname,
            "date": exam.date_humanreadable,
            "teachers": [teacher.name for teacher in exam.teachers],
            "description": exam.additional_info,
            "results": exam.results,
        }
    )


def isExamInDatabase(exam: Exam) -> bool:
    """
    Check if an exam is in the database.
    :param exam: Exam to be checked
    :return: True if the exam is in the database, False if it's not.
    """
    dbconn = pymongo.MongoClient(os.getenv("MONGO"), server_api=ServerApi('1'))
    db_exam_history = dbconn["examlib"]["history"]
    if db_exam_history.find_one(
            {
                "_id": exam.date_humanreadable + exam.name + exam.course_fullname
            }
    ) is None:
        return False
    else:
        return True
