from django.contrib.auth.backends import BaseBackend
from .models import Teacher

class TeacherBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            teacher = Teacher.objects.get(username=username)
            if teacher.check_password(password):
                return teacher
        except Teacher.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Teacher.objects.get(pk=user_id)
        except Teacher.DoesNotExist:
            return None