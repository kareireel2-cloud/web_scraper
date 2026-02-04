import asyncio
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Set

class AsyncScrapper:
    def __init__(self, max_concurrency: int):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.client = httpx.AsyncClient(timeout=10, follow_redirects=True, headers=headers)
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.visited: Set[str] = set()
        with open('ignored_ext.txt','r',encoding='utf-8') as file:
            self.blocked_extensions = [line.strip() for line in file if line.strip()]
        with open('blocked_sites.txt', 'r', encoding='utf-8') as file:
            self.blocked_sites = [line.strip() for line in file if line.strip()]
    
    async def close(self):
        await self.client.aclose()

    async def get_abs_url(self, url: str) -> List[str]:
        
        async with self.semaphore:
            # Проверка, был ли посещён сайт, чтобы не зациклиться в бесконечные переходы
            
            try:
                if url in self.visited:
                    return []
                self.visited.add(url)
                resp = await self.client.get(url)
                
                content_type = resp.headers.get('Content-Type','')
                if 'text/html' not in content_type:
                    return []

                if resp.status_code != 200:
                    return []

                soup = BeautifulSoup(resp.text, 'html.parser')
                links = soup.find_all('a', href=True)
                
                valid_urls = []
                for link in links:
                    clean_url = urljoin(url, link['href']).split('#')[0]
                    if self.is_valid_url(clean_url):
                        valid_urls.append(clean_url)
                return valid_urls
            except Exception as e:
                return []


    async def fetch_html(self, url: str) -> tuple[str, str]:
        async with self.semaphore:
            try:
                resp = await self.client.get(url)
                html = resp.text        
                return url, html.replace("\x00", "")
            except Exception as e:
                return url, ''
        
    def is_valid_url(self, url: str) -> bool:       
        
        # Проверка на расширение, если нужно убрать или добавить,список в файле igroned_ext.txt
        if any(url.endswith(ext) for ext in self.blocked_extensions):
            return False
        
        # Проверка, есть ли юрл в списке заблокированных в РФ сайтов
        if any(url.startswith(blocked) for blocked in self.blocked_sites):
            return False
        
        return True
    
    async def fetch_page(self, start_url: str, depth: int) -> list[tuple[str, str, str]]:
        current_level_urls = [start_url]
        all_found_urls = {start_url}

        for _ in range(depth):

            tasks = [self.get_abs_url(url) for url in current_level_urls]
            results = await asyncio.gather(*tasks)
                    
            next_level_urls = []
            for urls in results:
                for u in urls:
                    if u not in all_found_urls:
                        all_found_urls.add(u)
                        next_level_urls.append(u)
            
            current_level_urls = next_level_urls
            if not current_level_urls:
                break

        data: list[tuple[str, str, str]] = []
        tasks = [self.fetch_html(url) for url in current_level_urls]
        results = await asyncio.gather(*tasks)

        for url, html in results:
            soup = BeautifulSoup(html, "html.parser")
            title_tag = soup.find("title")
            title = title_tag.text if title_tag else ""
            data.append((url, title, html))

        return data

async def web_scraping_url(url,max_concurency,depth):
    scraper = AsyncScrapper(max_concurrency=max_concurency) 
    try:
        data = await scraper.fetch_page(url, depth)
        return data
    finally:
        await scraper.close()




