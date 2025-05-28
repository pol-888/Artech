from django.urls import path
from . import views 
from django.contrib import admin

urlpatterns = [
      path('admin/', admin.site.urls),
      path('home.html', views.home, name='home'),
      path('about.html', views.about, name='about'),
      path('createacc.html', views.createacc, name='createacc'),
      path('profile.html', views.profile, name='profile'),
      path('form.html', views.form, name='form'),
      path('login.html', views.login_view, name='login'),
      path('logout/', views.logout_view, name='logout'),
      path('userlist.html', views.user_list, name='userlist'),
      path('orderlist.html', views.order_list, name='order_list'),
      path('order/update/<int:order_id>/', views.order_update, name='order_update'),
      path('order/delete/<int:order_id>/', views.order_delete, name='order_delete'),
      path('forget_password.html', views.forget_password, name='forget_password'),
]
