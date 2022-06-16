from pydantic import BaseModel
from datetime import datetime
from typing import (
    Optional,
    List,
    ForwardRef
)

CommentWithChild = ForwardRef("CommentWithChild")

class User(BaseModel):

    id: int
    username: str
    date_created: datetime

    class Config:
        orm_mode = True


class UserCreate(BaseModel):

    username: str
    password: str

class UserUpdate(BaseModel):

    password: str

class UserLogin(BaseModel):

    username: str
    password: str


class Post(BaseModel):

    id: int
    title: str
    text: str
    date_created: datetime

    class Config:
        orm_mode = True


class PostCreate(BaseModel):

    title: str
    text: str

class PostUpdate(BaseModel):

    text: str

class PostToDB(BaseModel):

    title: str
    text: str
    user_id: int

class Comment(BaseModel):

    id: int
    text: str
    user_id: int
    post_id: int
    date_created: datetime
    parent_comment_id: Optional[int]

    class Config:
        orm_mode = True

class CommentWithChild(BaseModel):

    id: int
    text: str
    user_id: int
    post_id: int
    date_created: datetime
    parent_comment_id: Optional[int]
    child_comments: Optional[List[CommentWithChild]]

CommentWithChild.update_forward_refs()

class CommentCreate(BaseModel):

    text: str
    parent_comment_id: Optional[int]

class CommentToDB(BaseModel):

    text: str
    user_id: int
    post_id: int
    parent_comment_id: Optional[int]

class CommentUpdate(BaseModel):

    text: str

class AccessToken(BaseModel):

    access_token: str


class PostComment(BaseModel):

    id: int
    title: str
    text: str
    date_created: datetime
    comments: Optional[List[CommentWithChild]]