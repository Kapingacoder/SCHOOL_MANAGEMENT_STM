# ...existing code...
from django.shortcuts import render
from primary_dashboard.models import Event
from secondary_dashboard.models import DocumentUpload

def events_list(request):
    events = Event.objects.all().order_by('-date')
    return render(request, 'parent_dashboard/events.html', {'events': events})

def documents_list(request):
    documents = DocumentUpload.objects.filter(is_active=True).order_by('-uploaded_at')
    return render(request, 'parent_dashboard/documents.html', {'documents': documents})
