"""
URL configuration for TrilokBiller project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path,include
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin123/', admin.site.urls),
    path('login/', user_login, name='login'),
    path('', RedirectView.as_view(url='/home/', permanent=False)),
    path('home/', home, name='home'),
    path('aboutUs/', about, name='aboutUs'),
    path('contactUs/', contact , name = 'contactUs'),
    path('accounts/', include('accounts.urls')),
    path('logout/', user_logout, name='logout'),
    path('contact/submit/', contact_submit, name='contact_submit'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





