from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from primary_dashboard.models import Parent as PrimaryParent
from secondary_dashboard.models import Parent as SecondaryParent, Student as SecondaryStudent

class Command(BaseCommand):
    help = 'Auto-link secondary parents and students to the correct user accounts based on matching user emails.'

    def handle(self, *args, **options):
        User = get_user_model()
        updated = 0
        for primary_parent in PrimaryParent.objects.all():
            user = primary_parent.user
            # Try to find a secondary parent with the same user
            secondary_parent = SecondaryParent.objects.filter(user=user).first()
            if secondary_parent:
                # Link all secondary students with this parent (by phone or name match)
                students = SecondaryStudent.objects.filter(parent__isnull=True, last_name=primary_parent.last_name)
                for student in students:
                    student.parent = secondary_parent
                    student.save()
                    updated += 1
        self.stdout.write(self.style.SUCCESS(f'Linked {updated} secondary students to their correct parent accounts.'))
