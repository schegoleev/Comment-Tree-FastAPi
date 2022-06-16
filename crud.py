import schemas
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from starlette.status import HTTP_403_FORBIDDEN

from fastapi import (
    FastAPI,
    Request,
    Depends,
    HTTPException
)
from models import (
    User,
    Post,
    Comment
)
from auth import (
    is_authenticated,
    jwt_encode,
    get_jwt,
    get_user_from_jwt,
    UserPermission
)

app = FastAPI()

def recursive_comment(comment: Comment, session: Session):

    full_comment = schemas.CommentWithChild(id=comment.id, text=comment.text, user_id=comment.user_id,
                                            post_id=comment.post_id, date_created=comment.date_created,
                                            parent_comment_id=comment.parent_comment_id)

    child_comments = session.query(Comment).filter(Comment.parent_comment_id==comment.id).all()
    full_comment.child_comments = []

    for child_comment in child_comments:
        tmp_comment_list = recursive_comment(comment=child_comment, session=session)
        full_comment.child_comments.append(tmp_comment_list)

    return full_comment

"""---------------USER-----------------"""

@app.get("/users/", response_model=list[schemas.User], dependencies=[Depends(UserPermission())], tags=["Users"])
async def list_users(session: Session = Depends(get_db)):
    users = session.query(User).all()
    return users


@app.get("/users/userId={user_id}", response_model=schemas.User, dependencies=[Depends(UserPermission())], tags=["Users"])
async def get_user(user_id: int, session: Session = Depends(get_db)):
    user = session.query(User).get(user_id)
    return user

@app.patch("/users/", response_model=dict, dependencies=[Depends(UserPermission())], tags=["Users"])
async def change_password(body: schemas.UserUpdate, request: Request, session: Session = Depends(get_db)):
    jwt_token = get_jwt(request=request)
    user_id = get_user_from_jwt(jwt_token=jwt_token , session=session)
    user = session.query(User).get(user_id)
    user.password = body.password
    session.add(user)
    session.commit()

    return {"status": "Пароль изменён"}


"""---------------POST-----------------"""

# TODO: Как будет время добавить фильтры
@app.get("/posts/", response_model=list[schemas.Post], dependencies=[Depends(UserPermission())], tags=["Posts"])
async def list_posts(session: Session = Depends(get_db)):
    posts = session.query(Post).all()
    return posts

@app.post("/posts/", response_model=dict, dependencies=[Depends(UserPermission())], tags=["Posts"])
async def create_post(body: schemas.PostCreate, request: Request, session: Session = Depends(get_db)):
    jwt_token = get_jwt(request=request)
    user_id = get_user_from_jwt(jwt_token=jwt_token, session=session)
    post_to_db = schemas.PostToDB(title=body.title, text=body.text, user_id=user_id)
    try:
        post = Post(**post_to_db.dict())
        session.add(post)
        session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Ошибка при записи данных")

    return {"status": "success", "payload": {"id": post.id, "title": post.title}}

@app.get("/posts/postId={post_id}", response_model=schemas.PostComment, dependencies=[Depends(UserPermission())], tags=["Posts"])
async def get_post(post_id: int, session: Session = Depends(get_db)):
    post = session.query(Post).get(post_id)
    post_perform = schemas.PostComment(id=post.id, title=post.title, text=post.text, date_created=post.date_created)
    comments_for_post = session.query(Comment).filter(Comment.post_id==post.id).all()
    print(comments_for_post)
    post_perform.comments = []
    for comment in comments_for_post:
        if comment.parent_comment_id is None:
            post_perform.comments.append(recursive_comment(comment=comment, session=session))
    return post_perform


@app.patch("/posts/postId={post_id}", response_model=schemas.Post, dependencies=[Depends(UserPermission())], tags=["Posts"])
async def patch_post(post_id: int, body: schemas.PostUpdate, request: Request, session: Session = Depends(get_db)):
    jwt_token = get_jwt(request=request)
    user_id = get_user_from_jwt(jwt_token=jwt_token , session=session)
    post = session.query(Post).get(post_id)
    if user_id != post.user_id:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN , detail="Нельзя редактировать чужой пост")

    post.text = body.text
    session.add(post)
    session.commit()
    return post



"""------------COMMENT-----------"""

@app.post("/comments/postId={post_id}", response_model=dict, dependencies=[Depends(UserPermission())], tags=["Comments"])
async def create_comment(post_id: int, body: schemas.CommentCreate, request: Request, session: Session = Depends(get_db)):
    jwt_token = get_jwt(request=request)
    user_id = get_user_from_jwt(jwt_token=jwt_token, session=session)
    comment_to_db = schemas.CommentToDB(text=body.text, user_id=user_id, post_id=post_id)
    if body.parent_comment_id:
        comment_to_db.parent_comment_id = body.parent_comment_id
    comment = Comment(**comment_to_db.dict())
    session.add(comment)
    session.commit()

    return {"status": "success", "commentId": comment.id}

@app.patch("/comments/commentId={comment_id}", response_model=dict, dependencies=[Depends(UserPermission())], tags=["Comments"])
async def edit_comment(comment_id: int, body: schemas.CommentUpdate, request: Request, session: Session = Depends(get_db)):

    jwt_token = get_jwt(request=request)
    user_id = get_user_from_jwt(jwt_token=jwt_token, session=session)
    comment = session.query(Comment).get(comment_id)
    if user_id != comment.user_id:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Нельзя редактировать чужой комментарий")

    comment.text = body.text
    session.add(comment)
    session.commit()



"""------------REGISTER/LOGIN-----------"""

@app.post("/register/")
async def register(body: schemas.UserCreate, session: Session = Depends(get_db)):

    try:
        user = User(**body.dict())
        session.add(user)
        session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")

    return {"status": "success", "userId": user.id}

@app.post("/login/", response_model=schemas.AccessToken)
async def login(data: schemas.UserLogin, session: Session = Depends(get_db)):
    if not is_authenticated(data=data, session=session):
        raise HTTPException(status_code=400 , detail="Неправильный пароль или имя пользователя")
    user = session.query(User).filter(User.username== data.username).first()
    return {"access_token": jwt_encode(user_id=user.id)}
