from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from primary_dashboard.models import Parent as PrimaryParent, Student as PrimaryStudent
from secondary_dashboard.models import Parent as SecondaryParent, Student as SecondaryStudent

class Command(BaseCommand):
    help = 'Auto-link primary and secondary parents and students to the correct user accounts based on matching user, phone, or email.'

    def handle(self, *args, **options):
        User = get_user_model()
        updated_primary = 0
        updated_secondary = 0
        # Link secondary parents to primary parents by user
        for primary_parent in PrimaryParent.objects.all():
            user = primary_parent.user
            # Try to find a secondary parent with the same user
            secondary_parent = SecondaryParent.objects.filter(user=user).first()
            if not secondary_parent:
                # Try to match by phone or email if user is not set
                secondary_parent = SecondaryParent.objects.filter(phone=primary_parent.phone).first()
                if secondary_parent:
                    secondary_parent.user = user
                    secondary_parent.save()
            # Link secondary students to this parent if not already linked
            if secondary_parent:
                students = SecondaryStudent.objects.filter(parent__isnull=True, last_name=primary_parent.last_name)
                for student in students:
                    student.parent = secondary_parent
                    student.save()
                    updated_secondary += 1
        # Link primary parents to secondary parents by user
        for secondary_parent in SecondaryParent.objects.all():
            user = secondary_parent.user
            primary_parent = PrimaryParent.objects.filter(user=user).first()
            if not primary_parent:
                primary_parent = PrimaryParent.objects.filter(phone=secondary_parent.phone).first()
                if primary_parent:
                    primary_parent.user = user
                    primary_parent.save()
            if primary_parent:
                students = PrimaryStudent.objects.filter(parent__isnull=True, last_name=secondary_parent.last_name)
                for student in students:
                    student.parent = primary_parent
                    student.save()
                    updated_primary += 1
        self.stdout.write(self.style.SUCCESS(f'Linked {updated_primary} primary and {updated_secondary} secondary students to their correct parent accounts.'))
