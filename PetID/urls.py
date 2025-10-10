"""
URL configuration for PetID project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from core.views import ServeMediaView
from django.shortcuts import redirect

urlpatterns = [
    # ถ้าอยู่ path / ให้ redirect ไปที่ /core/
    path('', lambda request: redirect('/core/'), name='root_redirect'),
    path('admin/', admin.site.urls),
    path('core/', include('core.urls')),
    # Custom media serving for production
    # comment ตอน server-side
    # re_path(r'^media/(?P<path>.*)$', ServeMediaView.as_view(), name='serve_media'),
]

# สำหรับแสดงไฟล์ static files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Media files serving - ทำงานทั้ง development และ production
# ใน production nginx จะ handle /media/ แต่ fallback ไปที่ Django ถ้าจำเป็น
if settings.DEBUG:
    # Development: ใช้ Django's static file serving
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Production: ใช้ custom ServeMediaView สำหรับ fallback
    pass  # ServeMediaView ถูกกำหนดไว้แล้วด้านบน
