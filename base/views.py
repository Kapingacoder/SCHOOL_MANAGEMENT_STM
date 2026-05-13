from django.shortcuts import render, redirect

# Create your views here.
def homepage(request):
    return render(request, 'base/home.html')


from django.contrib.auth.decorators import login_required
from primary_dashboard.models import Student as PrimaryStudent, Parent as PrimaryParent
from secondary_dashboard.models import Student as SecondaryStudent, Parent as SecondaryParent

@login_required
def parent_all_children_results(request):
    user = request.user
    # Try to get parent profile from both dashboards
    primary_parent = PrimaryParent.objects.filter(user=user).first()
    secondary_parent = SecondaryParent.objects.filter(user=user).first()

    # Get all children from both dashboards
    primary_children = PrimaryStudent.objects.filter(parent=primary_parent) if primary_parent else []
    secondary_children = SecondaryStudent.objects.filter(parent=secondary_parent) if secondary_parent else []

    context = {
        'primary_children': primary_children,
        'secondary_children': secondary_children,
    }
    return render(request, 'base/parent_all_children_results.html', context)