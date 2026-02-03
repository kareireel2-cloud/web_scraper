from datetime import datetime
import asyncio
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Set




class AsyncScrapper:
    def __init__(self, max_concurrency: int):
        self.client = httpx.AsyncClient(timeout=10, follow_redirects=True)
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.visited: Set[str] = set()
        with open('blocked_sites.txt', 'r', encoding='utf-8') as file:
            self.blocked_sites = [line.strip() for line in file if line.strip()]
    
    async def close(self):
        await self.client.aclose()

    async def get_abs_url(self, url: str) -> List[str]:
        
        async with self.semaphore:
            try:
                # Проверка, был ли посещён сайт, чтобы не ходить по кругу
                # или находится в списке заблокированных сайтов.
                # Список заблокированных сайтов находится в файле blocked_sites.txt
                if url in self.visited or any(url.startswith(blocked_site) for blocked_site in self.blocked_sites):
                    return []
                self.visited.add(url)

                resp = await self.client.get(url)
                if resp.status_code != 200:
                    return []

                soup = BeautifulSoup(resp.text, 'html.parser')
                links = soup.find_all('a', href=True)
                
                valid_urls = []
                for link in links:
                    clean_url = urljoin(url, link['href']).split('#')[0]
                    if clean_url.startswith('http'):
                        valid_urls.append(clean_url)
                return valid_urls
            except Exception as e:
                # print(f"Ошибка при чтении {url}: {e}")
                return []


    async def fetch_html(self, url: str) -> tuple[str, str]:
        async with self.semaphore:
            try:
                resp = await self.client.get(url)
                html = resp.text
                soup = BeautifulSoup(html, "html.parser")
                title_tag = soup.find("title")
                title = title_tag.text if title_tag else ""
            except Exception as e:
                # print(f"Ошибка при чтении {url}: {e}")
                html = ""
        return url, html
        

    
    async def fetch_page(self, start_url: str, depth: int) -> list[tuple[str, str, str]]:
        current_level_urls = [start_url]
        all_found_urls = {start_url}

        for d in range(depth):
            # print(f"Обработка уровня {d}, найдено ссылок: {len(current_level_urls)}")
            
            tasks = [self.get_abs_url(url) for url in current_level_urls]
            results = await asyncio.gather(*tasks)
            
            # Собираем все найденные ссылки для следующего уровня
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



# url = 'https://pythonworld.ru/tipy-dannyx-v-python/isklyucheniya-v-python-konstrukciya-try-except-dlya-obrabotki-isklyuchenij.html'
async def get_data_from_url(url,max_concurency,depth):
    scraper = AsyncScrapper(max_concurrency=max_concurency) 
    try:
        data = await scraper.fetch_page(url, max_concurency, depth)
        return data
    finally:
        await scraper.close()


# if __name__ == '__main__':
#     asyncio.run(main(url,10))