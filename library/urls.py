from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    
    path('', views.search_book, name='opac'),
    path('api/reservations', views.reservation_api, name='reservation_api'),



    # path('book/search', views.search_book, name='book_search'),
    # path("book/form/", views.book_entry_form, name="book_entry_form"),
    
    
    
    
    # MARC21 routes    
    path('marc21/settings/rda', views.marc21_settings, name='marc21_settings_rda'),
    path('marc21/update/', views.update_marc21_field, name='update_marc21_field'),
    path('marc21/settings/', views.marc21_settings, name='marc21_settings'),
    
    
    
    # Department routes
    path('departments/', views.get_departments, name='get_departments'),
    
    
    # Program routes
    path('programs/', views.get_programs, name='get_programs'),


    path('ched/requirements', views.get_ched_requirements, name='ched-requirements'),


    #Book CRUD routes
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.book_create, name='book_create'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),

    path('books/<int:pk>/edit/', views.book_update, name='book_update'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),
 
    path('api/check-rfid/<str:rfid>/', views.check_rfid, name='check_rfid'),
    
    
    #Transaction CRUD routes
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/new/', views.transaction_create, name='transaction_create'),
    path('transaction-item/<int:pk>/checkout/', views.transaction_item_checkout, name='transaction_item_checkout'),
    path('transaction-item/<int:pk>/return/', views.transaction_item_return, name='transaction_item_return'),    
    path('transactions/<int:pk>/', views.transaction_detail, name='transaction_detail'),
    path('transactions/<int:pk>/checkout/', views.transaction_checkout, name='transaction_checkout'),
    path('transactions/<int:pk>/return/', views.transaction_return, name='transaction_return'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)