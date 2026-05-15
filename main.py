from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
import models, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def main_page():
    return FileResponse("templates/index.html")


@app.get("/comments")
def read_comments(search: Optional[str] = None, db: Session = Depends(get_db)):
    # 1. Получаем все комменты из базы, отсортированные по рейтингу
    all_comments = db.query(models.Comment).order_by(
        models.Comment.rating.desc(),
        models.Comment.created_at.desc()
    ).all()

    # 2. Если есть поисковый запрос, фильтруем список средствами Python
    if search:
        search_lower = search.lower()
        filtered_comments = [
            c for c in all_comments
            if search_lower in c.text.lower()
        ]
        return filtered_comments

    return all_comments


@app.post("/comments")
def create_comment(text: str, db: Session = Depends(get_db)):
    clean_text = text.strip()
    if not clean_text:
        raise HTTPException(status_code=400, detail="Текст пустой")

    exists = db.query(models.Comment).filter(models.Comment.text == clean_text).first()
    if exists:
        return exists

    new_comment = models.Comment(text=clean_text)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


@app.post("/comments/{comment_id}/vote")
def vote_comment(comment_id: int, delta: int, db: Session = Depends(get_db)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if comment:
        comment.rating += delta
        db.commit()
    return {"status": "ok"}


@app.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if comment:
        db.delete(comment)
        db.commit()
    return {"status": "deleted"}