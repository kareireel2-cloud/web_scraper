import asyncio
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class AsyncCrawler:
    def __init__(self, max_depth: int, max_concurrency: int):
        self.max_depth = max_depth
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.visited = set()
        self.results = []
        self.client = httpx.AsyncClient(timeout=10, follow_redirects=True)

    async def fetch_page(self, url: str, depth: int):
        # Проверяем глубину и уникальность URL
        if depth > self.max_depth or url in self.visited:
            return
        
        async with self.semaphore: # Ограничиваем до k одновременных запросов
            if url in self.visited: return # Двойная проверка после ожидания
            self.visited.add(url)
            
            try:
                print(f"[Depth {depth}] Fetching: {url}")
                response = await self.client.get(url)
                if response.status_code != 200:
                    return

                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.title.string if soup.title else "No Title"
                
                # Сохраняем результат
                self.results.append({"url": url, "title": title.strip(), "depth": depth})

                # Собираем ссылки для рекурсии
                if depth < self.max_depth:
                    tasks = []
                    for a in soup.find_all('a', href=True):
                        link = urljoin(url, a['href'])
                        # Фильтруем, чтобы не уходить на другие домены (опционально)
                        if urlparse(link).netloc == urlparse(url).netloc:
                            tasks.append(self.fetch_page(link, depth + 1))
                    
                    # Запускаем дочерние ссылки параллельно
                    if tasks:
                        await asyncio.gather(*tasks)

            except Exception as e:
                print(f"Error scraping {url}: {e}")

    async def run(self, start_url: str):
        await self.fetch_page(start_url, 0)
        await self.client.aclose()
        return self.results

# Запуск
async def main():
    N = 2  # Глубина
    K = 5  # Параллельность (одновременные URL)
    start_url = "https://ru.minecraft.wiki/w/%D0%9E%D0%BA%D0%B5%D0%B0%D0%BD"
    
    crawler = AsyncCrawler(max_depth=N, max_concurrency=K)
    data = await crawler.run(start_url)
    
    print(f"\nГотово! Собрано страниц: {len(data)}")

if __name__ == "__main__":
    asyncio.run(main())