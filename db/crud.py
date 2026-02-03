from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from service.main import get_data_from_url
from . import models

async def insert_new_data(session: AsyncSession,
        start_url:str,
        depth:int,
        max_concurency:int):
    data = await get_data_from_url(url=start_url, depth = depth, max_concurency = max_concurency)
    objs = [
        models.UrlData(
            url = url,
            title = title,
            html_body = html
        ) for (url, title, html) in data
    ]
    session.add_all(objs)
    await session.commit()



async def get_html_by_title(session: AsyncSession, title: str):
    stmt = select(models.UrlData).where(models.UrlData.title == title)
    result = await session.scalars(stmt)
    return result.first()

async def get_obj_by_url(session: AsyncSession, url:str):
    stmt = select(models.UrlData).where(models.UrlData.url == url)
    result = await session.scalars(stmt)
    return result.first()



# def get_data_from_url(session: Session, url: str) -> str:
#     scrapper = AsyncScrapper(max_concurrency=10)
#     data = scrapper.fetch_page(url, depth=2)
#     return data