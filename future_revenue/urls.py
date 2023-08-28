from django.urls import path
from future_revenue import views



urlpatterns = [
    path('', views.index, name='home'),
    # dashboard
    path('dashboard/login/', views.managerLogin, name='manager_login'),
    path('dashboard/logout/', views.managerLogout, name='manager_logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/profile/', views.managerProfile, name='profile'),
    path('dashboard/sales_data/', views.sales_data, name='sales_data'),
    path('dashboard/product_categories/', views.product_category, name='categories_list'),
    path('dashboard/product_list/', views.product_list, name='products_list'),
    path('dashboard/product_list/<int:product_id>/sales_trend/', views.sales_trend, name='sales_trend'),
    path('dashboard/product_list/<int:product_id>/predict_revenue/', views.predict_revenue, name='predict_revenue'),
]
