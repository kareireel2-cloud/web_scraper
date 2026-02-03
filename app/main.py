from contextlib import asynccontextmanager
from ast import Return
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Query, status
from pydantic import BaseModel, model_validator
from sqlalchemy.orm import Session

from db import crud, models
from db.session import Base, async_engine, get_db, AsyncSession
from . import schemas


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        # Важно: используем run_sync для синхронного метода create_all
        await conn.run_sync(Base.metadata.create_all)
    
    yield

    await async_engine.dispose()

app = FastAPI(title="Web Scraper API", lifespan=lifespan)


@app.post("/post_data")
async def post_data_from_url(
    url: str,
    depth: int,
    max_concurrency: int,
    db: AsyncSession = Depends(get_db),
    ):
    
    length = await crud.insert_new_data(
                        session = db,
                        start_url=url,
                        depth=depth,
                        max_concurency=max_concurrency,
    )
    return {
        'message': f'Найдено и сохранено {length} ссылок',
        'status':'success',
    }


@app.get("/search")
async def search(
    title: Optional[str] = None, 
    url: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    
    if title is None and url is None:
        raise HTTPException(
            status_code=400, 
            detail='Вы должны передать либо title, либо url'
        )
    
    if title:
        return await crud.get_html_by_title(title=title, session = db)
    elif url:
        return await crud.get_html_by_url(url=url, session=db)

@app.get('/get_list')
async def get_list(db: AsyncSession = Depends(get_db)):
    return await crud.get_list_of_urls_and_titles(session = db)