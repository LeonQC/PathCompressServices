import os
import django
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel, HttpUrl
from asgiref.sync import sync_to_async


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_django_project.settings')
django.setup()

@sync_to_async
def get_url_details_sync(short_code: str):
    try:
        return URLMapping.objects.get(short_code=short_code)
    except URLMapping.DoesNotExist:
        return None

from url_shortener.models import URLMapping
from url_shortener.services import (
    create_short_url,
    get_long_url,
    delete_url_mapping,
    update_url_mapping,
    list_url_mappings,
    get_long_url_sync
)

class URL(BaseModel):
    long_url: HttpUrl

class CreateURLResponse(BaseModel):
    long_url: HttpUrl
    short_code: str

app = FastAPI()

@app.post("/urls/", response_model=CreateURLResponse)
async def create_url(url: URL):
    url_mapping = await create_short_url(url.long_url)  # Assuming this is now an async function
    return CreateURLResponse(long_url=url_mapping.long_url, short_code=url_mapping.short_code)

@app.get("/urls/{short_code}/", response_model=URL)
async def get_url_details(short_code: str):
    url_details = await get_url_details_sync(short_code)
    if url_details:
        return URL(long_url=url_details.long_url, short_code=url_details.short_code)
    else:
        raise HTTPException(status_code=404, detail="URL not found")

@sync_to_async
def get_long_url_sync(short_code):
    try:
        url_mapping = URLMapping.objects.get(short_code=short_code)
        return url_mapping.long_url
    except URLMapping.DoesNotExist:
        return None

@app.get("/{short_code}/")
async def redirect_to_url(short_code: str):
    long_url = await get_long_url(short_code)  # Assuming this is now an async function
    if long_url:
        return RedirectResponse(url=long_url)
    else:
        raise HTTPException(status_code=404, detail="URL not found")

@app.delete("/urls/{short_code}", status_code=204)
async def delete_url(short_code: str):
    success = await delete_url_mapping(short_code)  # Assuming this is now an async function
    if success:
        return {"detail": "URL deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="URL not found")

@app.put("/urls/{short_code}", response_model=CreateURLResponse)
async def update_url(short_code: str, url: URL):
    updated_mapping = await update_url_mapping(short_code, url.long_url)  # Assuming this is now an async function
    if updated_mapping:
        return CreateURLResponse(long_url=updated_mapping.long_url, short_code=updated_mapping.short_code)
    else:
        raise HTTPException(status_code=404, detail="URL not found")

@app.get("/urls/", response_model=List[CreateURLResponse])
async def list_urls():
    urls_list = await list_url_mappings()  # Assuming this is now an async function
    return [CreateURLResponse(long_url=url.long_url, short_code=url.short_code) for url in urls_list]


@app.get("/test/")
async def test():
    return {"message": "Test route works!"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This is for development only, specify your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
