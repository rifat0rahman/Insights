from django.urls import path
from . import views

urlpatterns = [
    path('',views.timeline,name='timeline'),
    path('analysis/<name>/<option>/',views.analysis,name='analysis'),
    path('documentation',views.doc,name='doc'),

]
