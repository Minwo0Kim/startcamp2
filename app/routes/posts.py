from fastapi import APIRouter
from pydantic import BaseModel

from ..database import SessionLocal
from ..models import Post

posts_router = APIRouter(prefix = "/api/posts", tags = ["posts"])

#post 생성 요청 시 request body
class C_Post(BaseModel):
    title : str
    content : str
    password : str
    route_id : int | None = None

class U_Post(BaseModel):
    title : str
    content : str
    password : str

#후기/게시글 작성
@posts_router.post("")
async def create_post(post : C_Post):
    return {"message": post.title}

#전체 게시글 목록 조회
@posts_router.get("")
def get_posts():
    return {"message": "전체 리스트 출력"}

#게시글 상세 조회
@posts_router.get("/{post_id}")
def get_post():
    return {"message": "상세조회 완료"}

#게시글 수정
@posts_router.put("/{post_id}")
def fix_post():
    return {"message": "수정완료"}

#게시글 삭제
@posts_router.delete("/{post_id}")
def delete_post():
    return {"message": "삭제기능"}
