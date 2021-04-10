from django.contrib import admin
from django.urls import path, include

from app import views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('add/', views.add_transaction, name='add_transaction'),
    path('update/', views.update_transaction, name='update_transaction'),
    path('delete/', views.delete_transaction, name='delete_transaction'),
    path('get/', include('app.urls'))
]