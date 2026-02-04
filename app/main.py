from contextlib import asynccontextmanager
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Query
import json
from pydantic import AnyHttpUrl, Field
from sqlalchemy import desc
from db import crud
from db.session import Base, async_engine, get_db, AsyncSession

def load_desc(method_name:str):
    '''Функция, чтобы загрузить с файла текстовое описание метода.'''
    
    with open('description.json', 'r') as f:
        desc = json.load(f)
        if desc[method_name]:
            return desc[method_name] 
        else: 
            return ''
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_engine.dispose()

app = FastAPI(title="Web Scraper API", lifespan=lifespan)

@app.post("/post_data", description = load_desc('post_data_from_url'))
async def post_data_from_url(
    url: AnyHttpUrl,
    depth: int = Query(ge=0,le=6, description='Глубина скрапинга'),
    max_concurrency : int = Query(ge=0, description='Максимальное количество одновременно обрабатываемых сайтов'),
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

@app.get("/search", description=load_desc('search'))
async def search(
    title: Optional[str] = None, 
    url: Optional[AnyHttpUrl] = None,
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

@app.get('/get_list', description=load_desc('get_list'))
async def get_list(db: AsyncSession = Depends(get_db)):
    return await crud.get_list_of_urls_and_titles(session = db)