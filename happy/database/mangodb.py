import os, sys
sys.path.append(os.getcwd())

from dataclasses import dataclass, asdict, field
from pymongo import MongoClient
from datetime import datetime
from typing import Union
from happy.env import Keys

# Define a data class
@dataclass
class User:
    _id: str
    FullName: str
    Age: int
    Email: str
    Address: str
    Gender: str
    DOB: str
    Height: str
    InputLanguage: str
    AssistantVoice: str
    ContactNumber: str
    Password: str
    CreatedAt: datetime
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime

    def to_dict(self):
        return asdict(self)

@dataclass
class Session:
    StartedAt: datetime
    EndedAt: datetime
    Messages: list[Message] = field(default_factory=list)
    
    def to_dict(self):
        return asdict(self)


@dataclass
class History:
    _id: str
    CreatedAt: datetime
    LastModified: datetime
    Sessions: list[Session] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

    @property
    def messages(self):
        return [message.to_dict() for session in self.Sessions for message in session.Messages]


class MongoDB:
    def __init__(self):
        self.client = MongoClient(Keys.get("MongoUri"))
        self.db = self.client["Happy"]
        self.collection = self.db["Users"]
        self.messagescollection = self.db["Messages"]
    
    def getUsers(
        self, 
        _id: str = None, 
        FullName: str = None, 
        Age: int = None, 
        Email: str = None, 
        Address: str = None, 
        Gender: str = None, 
        DOB: str = None, 
        Height: str = None, 
        InputLanguage: str = None, 
        AssistantVoice: str = None, 
        ContactNumber: str = None, 
        Password: str = None, 
        CreatedAt: datetime = None
        ):
        """
        Retrieves a user or users based on the provided parameters.
        
        :param _id: Unique identifier for the user.
        :param FullName: Name of the user.
        :param Age: Age of the user.
        :param Email: Email address of the user.
        :param Address: Physical address of the user.
        :param Gender: Gender of the user.
        :param DOB: Date of birth of the user.
        :param Height: Height of the user.
        :param InputLanguage: Preferred input language of the user.
        :param AssistantVoice: Preferred voice for the assistant.
        :param ContactNumber: Contact number of the user.
        :param Password: Password of the user.
        :param CreatedAt: Date and time the user was created.
        :return: A list of users that match the criteria, each as a dictionary.
        """
        # Build the query dictionary from non-None parameters
        query = {k: v for k, v in locals().items() if k != 'self' and v is not None}
        
        # Query the database
        result = self.collection.find(query)
        return [User(**user) for user in result]

    def getUser(
        self, 
        _id: str = None, 
        FullName: str = None, 
        Age: int = None, 
        Email: str = None, 
        Address: str = None, 
        Gender: str = None, 
        DOB: str = None, 
        Height: str = None, 
        InputLanguage: str = None, 
        AssistantVoice: str = None, 
        ContactNumber: str = None, 
        Password: str = None, 
        CreatedAt: datetime = None
        ) -> Union[User, None]:
        """
        Retrieves a user or users based on the provided parameters.
        
        :param _id: Unique identifier for the user.
        :param FullName: Name of the user.
        :param Age: Age of the user.
        :param Email: Email address of the user.
        :param Address: Physical address of the user.
        :param Gender: Gender of the user.
        :param DOB: Date of birth of the user.
        :param Height: Height of the user.
        :param InputLanguage: Preferred input language of the user.
        :param AssistantVoice: Preferred voice for the assistant.
        :param ContactNumber: Contact number of the user.
        :param Password: Password of the user.
        :param CreatedAt: Date and time the user was created.
        :return: A list of users that match the criteria, each as a dictionary.
        """
        # Build the query dictionary from non-None parameters
        query = {k: v for k, v in locals().items() if k != 'self' and v is not None}
        
        # Query the database
        result = self.collection.find_one(query)
        return User(**result) if result else None
    
    def insertUser(self, user: User):
        """
        Inserts a user into the database.
        
        :param user: The user to insert.
        """
        self.collection.insert_one(user.to_dict())

    def updateUser(self, user: User):
        """
        Updates a user in the database.
        
        :param user: The user to update.
        """
        self.collection.update_one({"_id": user._id}, {"$set": user.to_dict()})
    
    
    def insertHistory(self, history: History):
        """
        Inserts a history into the database.
        
        :param history: The history to insert.
        """
        self.messagescollection.insert_one(history.to_dict())

    def updateHistory(self, history: History):
        """
        Updates a history in the database.
        
        :param history: The history to update.
        """
        self.messagescollection.update_one({"_id": history._id}, {"$set": history.to_dict()})
    
    def getHistory(
        self,
        _id: str = None
        ) -> Union[History, None]:
        """
        Retrieves a history based on the provided parameters.
        
        :param _id: Unique identifier for the history.
        :return: A list of history that match the criteria, each as a dictionary.
        """
        response = self.messagescollection.find_one({"_id": _id})
        return History(**response) if response else None
    
    def getSessions(
        self,
        _id: str = None,
        n: int = None
        ) -> Union[list[Session], None]:
        """
        Retrieves the last n sessions based on the provided parameters.
        
        :param _id: Unique identifier for the history.
        :param n: Number of sessions to retrieve.
        :return: A list of the last n sessions.
        """
        # Project only the needed fields to avoid loading unnecessary data
        projection = {
            "_id": 0,  # Exclude the _id from the result
            "Sessions": {"$slice": -n} if n else 1  # Slice the last n sessions
        }

        # Query the database for the specific sessions using the _id and projection
        response = self.messagescollection.find_one({"_id": _id}, projection)
        
        if response and "Sessions" in response:
            # Convert the sessions to a list of Session objects
            sessions = [Session(**session) for session in response["Sessions"]]
            return sessions if sessions else None
        else:
            return None
    
    def countUsers(self) -> int:
        """
        Counts the number of users in the database.
        
        :return: The number of users in the database.
        """
        return self.collection.count_documents({})
    
    def insertSession(self, _id: str, session: Session):
        """
        Inserts a session into the database.
        
        :param session: The session to insert.
        """
        self.messagescollection.update_one({"_id": _id}, {"$push": {"Sessions": session.to_dict()}})

    def sessionsToMessages(self, sessions: list[Session], rmtimestamp: bool = True) -> list[Message]:
        """
        Converts a list of sessions to a History object.
        
        :param sessions: The list of sessions to convert.
        :return: The History object created from the sessions.
        """
        if rmtimestamp:
            tmp = [message for session in sessions for message in (session.Messages if type(session) == Session else session["Messages"])]
            new = []
            for message in tmp:
                new.append({"role": message["role"], "content": message["content"]})
            return new
                
        else:
            return [message for session in sessions for message in (session.Messages if type(session) == Session else session["Messages"])]


if __name__ == "__main__":
    from rich import print
    db = MongoDB()
    # db.client["Happy"]["Messages"].insert_one(
    #     History(
    #         "Divyansh",
    #         datetime.now(),
    #         datetime.now(),
    #         [
    #             Session(
    #                 datetime.now(),
    #                 datetime.now(),
    #                 [
    #                     Message("user", "Hi", datetime.now()),
    #                     Message("user", "Hello", datetime.now()),
    #                     Message("user", "Hellos", datetime.now()),
    #                     Message("user", "Hellodas", datetime.now())
    #                 ]
    #             ),
    #             Session(
    #                 datetime.now(),
    #                 datetime.now(),
    #                 [
    #                     Message("user", "His2", datetime.now()),
    #                     Message("user", "Hellos2", datetime.now()),
    #                     Message("user", "Helloss2", datetime.now()),
    #                     Message("user", "Hellodas2s", datetime.now())
    #                 ]
    #             )
    #         ]
    #         ).to_dict()
    #     )
    # c = MongoDB()
    # sesss= c.getSessions("Divyansh",4)
    # print(sesss)
    # # print([i for i in MongoDB().collection.find({})])
    # ms = c.sessionsToMessages(sesss)
    # print(ms)
    
    print(db.updateUser(User(_id = "ce9e2395d9bb531114994a699803382e88d67676d9f0abb326659ed3fd970142", FullName = "Divyansh")))