import random
import string
from asgiref.sync import sync_to_async
from .models import URLMapping
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def parse_website_details(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.find('title').get_text() if soup.title else 'No Title'
        favicon = soup.find('link', rel='shortcut icon')

        if favicon and 'href' in favicon.attrs:
            favicon_url = urljoin(url, favicon['href'])
        else:
            favicon_url = ''

        return title, favicon_url
    except requests.RequestException as e:
        # 网络请求错误处理
        print(f"Request error: {e}")
        return 'Error', ''
    except Exception as e:
        # 其他错误处理
        print(f"Error parsing website details: {e}")
        return 'Error', ''


def generate_short_code(k=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=k))

@sync_to_async
def create_short_url_sync(long_url, custom_short_code=None):
    # 如果用户提供了自定义短码，先检查是否已存在
    if custom_short_code:
        if URLMapping.objects.filter(short_code=custom_short_code).exists():
            raise ValueError("This short code is already in use.")
        short_code = custom_short_code
    else:
        short_code = generate_short_code()
        while URLMapping.objects.filter(short_code=short_code).exists():
            short_code = generate_short_code()

    title, favicon_url = parse_website_details(long_url)  # 调用网页解析函数
    url_mapping = URLMapping.objects.create(
        short_code=short_code,
        long_url=long_url,
        title=title,  # 假设你的模型中有一个 title 字段
        favicon=favicon_url  # 假设你的模型中有一个 favicon 字段
    )
    return url_mapping

async def create_short_url(long_url, custom_short_code=None):
    return await create_short_url_sync(long_url, custom_short_code)


@sync_to_async
def get_long_url_sync(short_code):
    try:
        url_mapping = URLMapping.objects.get(short_code=short_code)
        return url_mapping.long_url
    except URLMapping.DoesNotExist:
        return None

async def get_long_url(short_code):
    return await get_long_url_sync(short_code)

@sync_to_async
def list_url_mappings_sync():
    return list(URLMapping.objects.all())

async def list_url_mappings():
    return await list_url_mappings_sync()

@sync_to_async
def delete_url_mapping_sync(short_code):
    try:
        url_mapping = URLMapping.objects.get(short_code=short_code)
        url_mapping.delete()
        return True
    except URLMapping.DoesNotExist:
        return False

async def delete_url_mapping(short_code):
    return await delete_url_mapping_sync(short_code)

@sync_to_async
def update_url_mapping_sync(short_code, new_long_url):
    try:
        url_mapping = URLMapping.objects.get(short_code=short_code)
        url_mapping.long_url = new_long_url
        url_mapping.save()
        return url_mapping
    except URLMapping.DoesNotExist:
        return None

async def update_url_mapping(short_code, new_long_url):
    return await update_url_mapping_sync(short_code, new_long_url)
