import os
import re
import time
import json
import logging
from pathlib import Path
from urllib.parse import urlparse, urljoin, unquote
from urllib.robotparser import RobotFileParser
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import html2text

class HKTLoraCrawler:
    """
    一个用于爬取 hktlora.com 网站信息的网络爬虫。

    该爬虫会从网站的 sitemap 开始，抓取所有链接的页面内容，
    提取标题、描述和主要内容，并将其保存为 Markdown 文件。
    它会遵守 robots.txt 规则，并记录详细的日志。
    """
    def __init__(self, output_dir="e:\\knowledge\\notes\\hktlora", delay=1, retries=3, backoff_factor=0.5):
        """
        初始化爬虫。

        Args:
            output_dir (str): 保存爬取内容的目录。
            delay (int): 两次请求之间的延迟（秒）。
            retries (int): 请求失败时的重试次数。
            backoff_factor (float): 重试之间的退避因子。
        """
        self.base_url = "https://www.hktlora.com/"
        self.output_dir = Path(output_dir)
        self.delay = delay
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.visited_urls = set()
        self.success_count = 0
        self.failed_urls = []
        
        # 初始化 html2text
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        self.html_converter.body_width = 0

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 设置日志
        log_dir = Path("e:\\knowledge\\logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = log_dir / "hktlora_crawler.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.log_file, mode='w', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # 设置 Robots 解析器
        self.robot_parser = RobotFileParser()
        self.robot_parser.set_url(urljoin(self.base_url, "robots.txt"))
        try:
            self.robot_parser.read()
        except Exception as e:
            self.logger.error(f"无法读取 robots.txt: {e}")

    def _make_request(self, url, timeout=15):
        """
        发起一个带重试逻辑的 HTTP GET 请求。

        Args:
            url (str): 目标 URL。
            timeout (int): 请求超时时间。

        Returns:
            requests.Response or None: 成功则返回响应对象，否则返回 None。
        """
        for attempt in range(self.retries):
            try:
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                self.logger.warning(f"请求失败 (第 {attempt + 1}/{self.retries} 次): {url} - {e}")
                if attempt < self.retries - 1:
                    sleep_time = self.delay + (self.backoff_factor * (2 ** attempt))
                    self.logger.info(f"将在 {sleep_time:.2f} 秒后重试...")
                    time.sleep(sleep_time)
                else:
                    self.logger.error(f"请求失败，已达最大重试次数: {url}")
                    return None


    def can_fetch(self, url):
        """
        检查是否可以根据 robots.txt 爬取 URL。

        Args:
            url (str): 要检查的 URL。

        Returns:
            bool: 如果可以爬取则返回 True，否则返回 False。
        """
        try:
            return self.robot_parser.can_fetch("*", url)
        except Exception as e:
            self.logger.error(f"检查 robots.txt 失败 {url}: {e}")
            return False

    def _get_urls_from_sitemap(self, sitemap_url):
        """
        从单个 sitemap 文件中提取 URL。

        Args:
            sitemap_url (str): sitemap 的 URL。

        Returns:
            list: 从 sitemap 中提取的 URL 列表。
        """
        urls = []
        try:
            self.logger.info(f"正在解析 Sitemap: {sitemap_url}")
            response = self._make_request(sitemap_url, timeout=10)
            if not response:
                return urls
            
            soup = BeautifulSoup(response.content, "xml")
            for loc in soup.find_all("loc"):
                urls.append(loc.text)
        except requests.RequestException as e:
            self.logger.error(f"获取或解析 Sitemap 失败 {sitemap_url}: {e}")
        return urls

    def get_all_page_urls_from_sitemaps(self):
        """
        从根 sitemap 开始，递归解析所有 sitemap，返回所有非 sitemap 的页面 URL。

        Returns:
            list: 所有页面的 URL 列表。
        """
        root_sitemap_url = urljoin(self.base_url, "sitemap.xml")
        sitemaps_to_process = [root_sitemap_url]
        all_page_urls = []
        processed_sitemaps = set()

        while sitemaps_to_process:
            current_sitemap = sitemaps_to_process.pop(0)
            if current_sitemap in processed_sitemaps:
                continue

            urls = self._get_urls_from_sitemap(current_sitemap)
            processed_sitemaps.add(current_sitemap)

            for url in urls:
                if url.endswith(".xml"):
                    if url not in processed_sitemaps:
                        sitemaps_to_process.append(url)
                else:
                    all_page_urls.append(url)
        
        return list(set(all_page_urls)) # 返回去重后的列表

    def extract_content(self, url):
        """
        从给定的 URL 提取内容。

        Args:
            url (str): 要提取内容的 URL。

        Returns:
            dict: 包含标题、摘要、内容、URL 和时间戳的字典，如果失败则返回 None。
        """
        try:
            response = self._make_request(url, timeout=15)
            if not response:
                return None

            soup = BeautifulSoup(response.content, 'html.parser')

            title = soup.title.string if soup.title else "无标题"
            
            summary = ""
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc:
                summary = meta_desc.get("content", "")

            main_content_html = self.extract_main_content(soup, url)
            
            if not summary and main_content_html:
                # 如果没有 meta description，从正文第一段生成
                summary = ' '.join(main_content_html.splitlines()[:2])


            return {
                "title": title.strip(),
                "summary": summary.strip(),
                "content": main_content_html.strip(),
                "url": url,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        except requests.RequestException as e:
            self.logger.error(f"请求失败 {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"提取内容失败 {url}: {e}")
            return None

    def extract_main_content(self, soup, url):
        """
        从 BeautifulSoup 对象中提取主要内容并转换为 Markdown。
        采用“先定位，后清理”的策略。

        Args:
            soup (BeautifulSoup): 页面的 BeautifulSoup 对象。
            url (str): 当前页面的 URL，用于调试。

        Returns:
            str: 提取并转换后的 Markdown 文本。
        """
        # 1. 定位主要内容容器
        main_content_selectors = [
            "[data-elementor-type='wp-post']", ".elementor-widget-theme-post-content", 
            "main", "article", ".product-detail", ".elementor-section-wrap"
        ]
        
        main_content_element = None
        for selector in main_content_selectors:
            main_content_element = soup.select_one(selector)
            if main_content_element:
                self.logger.info(f"找到主要内容容器: '{selector}'")
                break
        
        if not main_content_element:
            self.logger.warning("未找到明确的主要内容容器，将使用 body 作为回退。")
            main_content_element = soup.body
            if not main_content_element:
                self.logger.error("连 body 标签都未找到，无法提取内容。")
                return ""

        # 2. 在定位到的容器内部进行清理
        selectors_to_remove = [
            # 导航和页眉页脚
            ".elementor-location-header", ".elementor-location-footer",
            "[role='navigation']", ".jet-nav", ".elementor-nav-menu",
            "header", "footer", "nav", "aside", ".sidebar",
            "#top-panel", ".breadcrumb",
            
            # Elementor 特有的无关小部件
            ".elementor-post-navigation", # 上一篇/下一篇
            ".elementor-widget-posts", # 相关文章/最新文章列表
            ".elementor-widget-archive-posts", # 存档文章列表
            ".elementor-widget-search-form", # 搜索框
            ".elementor-widget-share-buttons", # 分享按钮
            
            # 通用社交和评论区
            ".related-posts", ".comments-area", ".share-buttons",
        ]
        for selector in selectors_to_remove:
            for element in main_content_element.select(selector):
                element.decompose()



        # 3. 使用 html2text 进行转换
        html = str(main_content_element)
        markdown = self.html_converter.handle(html)
        
        # 4. 清理和格式化 Markdown
        content = '\n'.join(line.strip() for line in markdown.split('\n'))
        content = re.sub(r'\n{3,}', '\n\n', content) # 替换3个以上换行为2个
        return content.strip()

    def url_to_filepath(self, url):
        """
        将 URL 转换为文件路径，确保目录结构正确。

        Args:
            url (str): URL。

        Returns:
            Path: 文件路径。
        """
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        
        if not path:
            return self.output_dir / "index.md"
        
        # 解码 URL 路径中的特殊字符（如 %20）
        path_parts = [unquote(part) for part in path.split('/') if part]
        
        # 如果路径为空（例如 "example.com/"），则返回根目录的 index.md
        if not path_parts:
             return self.output_dir / "index.md"

        # 如果路径的最后一部分看起来像一个文件
        if '.' in path_parts[-1]:
            # 移除扩展名，并准备将其作为目录
            filename = Path(path_parts[-1]).stem
            path_parts[-1] = filename
        
        # 将路径部分连接起来，并在末尾添加 index.md
        filepath = self.output_dir.joinpath(*path_parts, "index.md")
        
        # 确保父目录存在
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        return filepath

    def save_content(self, content_data):
        """
        保存内容到文件。

        Args:
            content_data (dict): 内容数据。

        Returns:
            bool: 是否成功。
        """
        if not content_data or not content_data.get('content'):
            self.logger.warning(f"内容为空，跳过保存: {content_data.get('url')}")
            return False
        
        try:
            filepath = self.url_to_filepath(content_data['url'])
            
            markdown_content = f"""# {content_data['title']}

## 网页概要介绍

{content_data['summary']}

## 网页详细介绍

{content_data['content']}

---

**来源URL:** {content_data['url']}  
**抓取时间:** {content_data['timestamp']}
"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            self.logger.info(f"保存成功: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存失败 {content_data['url']}: {e}")
            return False

    def crawl_url(self, url):
        """
        爬取单个 URL。

        Args:
            url (str): 要爬取的URL。

        Returns:
            bool: 是否成功。
        """
        if url in self.visited_urls:
            return True
        
        if not self.can_fetch(url):
            self.logger.info(f"根据 robots.txt 跳过: {url}")
            return True # 认为是成功处理，因为我们遵守了规则

        self.visited_urls.add(url)
        
        try:
            self.logger.info(f"正在爬取: {url}")
            
            content_data = self.extract_content(url)
            
            if content_data:
                if self.save_content(content_data):
                    self.success_count += 1
                    return True
                else:
                    self.failed_urls.append(url)
                    return False
            else:
                self.failed_urls.append(url)
                return False
                
        except Exception as e:
            self.logger.error(f"爬取失败 {url}: {e}")
            self.failed_urls.append(url)
            return False
        finally:
            time.sleep(self.delay)

    def run(self, max_urls=None, debug_urls=None):
        """
        运行爬虫。

        Args:
            max_urls (int): 最大爬取URL数量，None表示不限制。
            debug_urls (list): 一个包含特定URL的列表，用于调试，如果提供，则只爬取这些URL。
        """
        self.logger.info("开始爬取华宽通网站...")
        
        if debug_urls:
            urls = debug_urls
            self.logger.info(f"进入调试模式，仅处理 {len(urls)} 个指定URL")
        else:
            urls = self.get_all_page_urls_from_sitemaps()
            self.logger.info(f"从所有 Sitemap 中获取到 {len(urls)} 个唯一页面 URL")

            # 过滤掉非 HTML 页面的 URL
            excluded_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip', '.mp4', '.mov', '.svg', '.webp')
            urls = [u for u in urls if not u.lower().endswith(excluded_extensions)]
            self.logger.info(f"过滤后剩余 {len(urls)} 个有效页面 URL")
            
            if not urls:
                self.logger.warning("Sitemap 为空或无法访问，尝试从首页开始爬取。")
                urls = [self.base_url]

            if max_urls:
                urls = urls[:max_urls]
                self.logger.info(f"限制爬取数量为 {max_urls} 个 URL")
        
        start_time = time.time()
        
        for i, url in enumerate(urls, 1):
            self.logger.info(f"进度: {i}/{len(urls)}")
            self.crawl_url(url)
        
        duration = time.time() - start_time
        self.generate_report(duration)

    def generate_report(self, duration):
        """
        生成爬取报告。

        Args:
            duration (float): 爬取耗时（秒）。
        """
        report = {
            'total_urls_processed': len(self.visited_urls),
            'success_count': self.success_count,
            'failed_count': len(self.failed_urls),
            'failed_urls': self.failed_urls,
            'duration_seconds': duration,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        report_file = self.output_dir / "crawl_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.logger.info("爬取完成！")
        self.logger.info(f"总处理URL数: {report['total_urls_processed']}")
        self.logger.info(f"成功: {report['success_count']}")
        self.logger.info(f"失败: {report['failed_count']}")
        self.logger.info(f"耗时: {duration:.2f} 秒")
        
        if self.failed_urls:
            self.logger.warning(f"失败的URL: {self.failed_urls}")

def main():
    """
    主函数，用于启动爬虫。
    """
    crawler = HKTLoraCrawler()
    # 运行全站爬取
    crawler.run()


if __name__ == "__main__":
    main()
