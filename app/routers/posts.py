from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import SessionLocal
from ..models import Post
from ..schemas import C_Post, C_PostResponse, R_AllPostResponse, R_PostResponse, U_Post, D_Post

posts_router = APIRouter(prefix = "/api/posts", tags = ["posts"])

def get_db():
    db = SessionLocal()
    try :
        yield db
    finally :
        db.close()

#후기/게시글 작성
@posts_router.post("", response_model=C_PostResponse)
async def create_post(post : C_Post, db : Session = Depends(get_db)):
    new_post = Post(
        title = post.title, 
        content = post.content, 
        password = post.password, 
        route_id = post.route_id
        )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"post_id": new_post.id, "message": "게시글 작성 완료"}

#전체 게시글 목록 조회
@posts_router.get("")
def get_posts():
    return {"message": "전체 리스트 출력"}

#게시글 상세 조회
@posts_router.get("/{post_id}", response_model = R_PostResponse)
async def get_post(post_id : int, db : Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is not None:
        return {"post_id" : post.id, "title" : post.title, "content" : post.content, "route_id" : post.route_id, "created_at" : post.created_at}
    else :
        return HTTPException(status_code=404, detail = "삭제되었거나, 존재하지 않는 게시물입니다.")

#게시글 수정
@posts_router.put("/{post_id}")
def fix_post(post_id : int, mod_post : U_Post, db : Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post.password != mod_post.password:
        return {"message": "비밀번호 불일치"}
    else :
        post.title = mod_post.title
        post.content = mod_post.content
        db.add(post)
        db.commit()

#게시글 삭제
@posts_router.delete("/{post_id}")
async def delete_post(post_id : int, del_post : D_Post, db : Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is not None:
        if post.password == del_post.password:
            db.delete(post)
            db.commit()
            return {"message" : "삭제 완료"}
        else :
            return {"message" : "비밀번호 불일치로 인해 삭제 불가"}
    else :
        return HTTPException(status_code=404, detail = "이미 삭제되었거나, 존재하지 않는 게시물입니다.")
    

# 이건 커밋 안했는데 들어갈까?