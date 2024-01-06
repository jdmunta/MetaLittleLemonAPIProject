from django.urls import path 
from . import views 
  
urlpatterns = [ 
    path('menu-items', views.MenuItemsViewSet.as_view({'get':'list', 'post':'create'})),
    path('menu-items/<int:pk>',views.MenuItemsViewSet.as_view({'get':'retrieve','put':'update','patch':'update','delete':'destroy'})),
    path('orders', views.OrdersViewSet.as_view({'get':'list','post':'create'})),
    path('orders/<int:pk>', views.OrdersViewSet.as_view({'get':'retrieve','put':'update','patch':'update','delete':'destroy'})),
    path('cart/menu-items', views.CartViewSet.as_view({'get':'list','post':'create','delete':'destroy'})),
    path('groups', views.GroupsViewSet.as_view({'get':'list','post':'create'})),
    path('groups/<str:groupname>/users', views.groups),
    path('groups/<str:groupname>/users/<str:username>', views.groups),
     
] 