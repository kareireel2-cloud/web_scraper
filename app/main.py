from ast import Return
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Query, status
from pydantic import BaseModel, model_validator
from sqlalchemy.orm import Session

from db import crud
from db.session import Base, async_engine, get_db
from . import schemas

Base.metadata.create_all(bind=async_engine)

app = FastAPI(title="Web Scraper API")


@app.post("/post_data")
async def post_data_from_url(
    url: str,
    depth: int,
    max_concurrency: int,
    ) -> str:
    
    crud.insert_new_data(start_url=url,
                        depth=depth,
                        max_concurency=max_concurrency,
    )


@app.get("/search")
async def search(
    title: Optional[str] = None, 
    url: Optional[str] = None
):
    
    if title is None and url is None:
        raise HTTPException(
            status_code=400, 
            detail='Вы должны передать либо title, либо url'
        )
    
    if title:
        return crud.get_html_by_title(title=title)
    elif url:
        return crud.get_data_from_url(url=url)