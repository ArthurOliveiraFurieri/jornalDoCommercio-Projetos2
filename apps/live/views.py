from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import LiveEvent


class LiveListView(ListView):
    model = LiveEvent
    template_name = 'live/list.html'
    context_object_name = 'events'

    def get_queryset(self):
        return LiveEvent.objects.filter(is_active=True)
