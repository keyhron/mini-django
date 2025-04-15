from django.urls import path
from . import views

urlpatterns = [ 
    path('', views.home, name="home"),
    path('categories', views.home, name="categories"),
    # path('hubs', views.home, name="hubs"),
    
    path('create-product/', views.createProduct, name="create-product"),
    # path('create-category/', views.createProduct, name="create-category"),
    # path('create-hub/', views.createProduct, name="create-hub"),
    
    path('update-product/<str:pk>/', views.updateProduct, name="update-product"),
    # path('update-category/<str:pk>/', views.updateProduct, name="update-category"),
    # path('update-hub/<str:pk>/', views.updateProduct, name="update-hub"),
    
    path('delete-product/<str:pk>/', views.deleteProduct, name="delete-product"), 
    # path('delete-category/<str:pk>/', views.deleteProduct, name="delete-category"), 
    # path('delete-hub/<str:pk>/', views.deleteProduct, name="delete-hub"), 
    
    path('import-products/', views.importProducts, name="import-products"),
    path('export-products/', views.exportProducts, name='export-products'),
]
