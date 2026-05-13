from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from secondary_dashboard.models import Parent

class Command(BaseCommand):
    help = 'Assigns a unique user with username to all secondary parents who do not have one.'

    def handle(self, *args, **options):
        UserModel = get_user_model()
        updated = 0
        for parent in Parent.objects.filter(user__isnull=True):
            names = [parent.first_name.lower(), parent.middle_name.lower() if parent.middle_name else None, parent.last_name.lower()]
            username = '_'.join(filter(None, names))
            user = UserModel.objects.create(username=username)
            user.set_unusable_password()
            user.save()
            parent.user = user
            parent.save()
            updated += 1
        self.stdout.write(self.style.SUCCESS(f"Assigned usernames to {updated} parents."))
