# url_shortener/models.py

from django.db import models

class URLMapping(models.Model):
    short_code = models.CharField(max_length=6, unique=True)
    long_url = models.URLField()
    title = models.CharField(max_length=255, blank=True, null=True)  # 添加标题字段
    favicon = models.URLField(blank=True, null=True)  # 添加图标 URL 字段
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.short_code}: {self.long_url}"
