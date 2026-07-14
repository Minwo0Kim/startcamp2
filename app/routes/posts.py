from fastapi import APIRouter

posts_router = APIRouter(prefix = "/api/posts", tags = ["posts"])

#후기/게시글 작성
@posts_router.post("")
def create_post():
    
#전체 게시글 목록 조회
@posts_router.get("")

#게시글 상세 조회
@posts_router.get("/{post_id}")

#게시글 수정
@posts_router.put("/{post_id}")

#게시글 삭제
@posts_router.delete("/{post_id}")