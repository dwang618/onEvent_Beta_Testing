from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("logout/", views.logout_view, name="logout"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.image_upload, name='upload'),
    path('upload/<int:upload_id>/', views.upload_details, name='upload_details'),
    path('delete/<int:upload_id>/', views.delete_upload, name='delete_upload'),
    path('dashboard/', views.event_list, name='event_list'),
    path('dashboard/<int:event_id>/', views.event_details, name='event_details'),
    path('add_event/', views.add_event, name='add_event'),
    path('edit_event/<int:event_id>/', views.edit_event, name='edit_event'),
    path('delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]


