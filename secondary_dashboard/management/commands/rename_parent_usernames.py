from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from secondary_dashboard.models import Parent

def generate_username(first_name, middle_name, last_name, existing_usernames):
    names = [first_name.lower(), middle_name.lower() if middle_name else None, last_name.lower()]
    username = '_'.join(filter(None, names))
    return username

class Command(BaseCommand):
    help = 'Renames all parent usernames in secondary to the new format (first_last1, first_last2, ...)' 

    def handle(self, *args, **options):
        UserModel = get_user_model()
        parents = Parent.objects.exclude(user__isnull=True)
        existing_usernames = set(UserModel.objects.values_list('username', flat=True))
        updated = 0
        for parent in parents:
            user = parent.user
            if user:
                new_username = generate_username(parent.first_name, parent.middle_name, parent.last_name, existing_usernames)
                if user.username != new_username:
                    user.username = new_username
                    user.save()
                    existing_usernames.add(new_username)
                    updated += 1
        self.stdout.write(self.style.SUCCESS(f"Updated {updated} parent usernames to new format."))
