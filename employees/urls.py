from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('employees/', views.employee_list_view, name='list'),
    path('employees/<int:pk>/', views.employee_detail_view, name='detail'),
    path('logout/', views.logout_view, name='custom_logout'),
]
