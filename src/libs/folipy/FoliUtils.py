import datetime
import os

import pymongo
from pymongo.server_api import ServerApi


def pushMessageToDatabase(dict: dict):
    """
    Push an announcement to the database.
    :param dict: Announcement to be pushed
    """
    # get the date
    dbconn = pymongo.MongoClient(os.getenv("MONGO"), server_api=ServerApi('1'))
    db_foliannouncements = dbconn["folilib"]["announcements"]
    try:
        db_foliannouncements.insert_one(
            {
                "_id": dict["message_id"],
                "cause": dict["cause"],
                "header": dict["header"],
                "message": dict["message"],
                "information": dict["information"],
                "date": datetime.datetime.now()
            }
        )
    except:
        db_foliannouncements.insert_one(
            {
                "_id": dict["message_id"],
            }
        )


def isAnnouncementInDatabase(dict: dict) -> bool:
    """
    Check if an announcement is in the database.
    :param dict: Announcement to be checked
    :return: True if the Announcement is in the database, False if it's not.
    """
    dbconn = pymongo.MongoClient(os.getenv("MONGO"), server_api=ServerApi('1'))
    db_foliannouncements = dbconn["folilib"]["announcements"]
    if db_foliannouncements.find_one(
            {
                "_id": dict["message_id"]
            }
    ) is None:
        return False
    else:
        return True
