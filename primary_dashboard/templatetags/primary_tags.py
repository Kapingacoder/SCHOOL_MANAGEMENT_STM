from django import template
from primary_dashboard.models import Class, Mark, Grade, Student
from django.db.models import Sum

register = template.Library()

@register.simple_tag
def get_primary_classes():
    """
    Fetches all Class objects from the database.
    """
    return Class.objects.all()

@register.simple_tag
def get_student_total_marks(student, term, year):
    """
    Calculates the total marks for a given student, term, and year.
    """
    total_marks = Mark.objects.filter(
        student=student,
        term=term,
        year=year
    ).aggregate(total=Sum('score'))['total']
    return total_marks or 0

@register.simple_tag
def get_grade_and_comment(score, total_marks):
    """
    Determines the grade and comment based on the student's score.
    """
    if total_marks == 0:
        percentage = 0
    else:
        percentage = (score / total_marks) * 100

    try:
        grade = Grade.objects.filter(
            min_score__lte=percentage,
            max_score__gte=percentage
        ).first()
        if grade:
            return f"{grade.grade} - {grade.comment}"
    except Grade.DoesNotExist:
        pass
    return "N/A"

@register.simple_tag
def get_subject_total(student, subject, term, year):
    """
    Calculates the total score for a given subject.
    """
    total_score = Mark.objects.filter(
        student=student,
        subject=subject,
        term=term,
        year=year
    ).aggregate(total=Sum('score'))['total']
    return total_score or 0