from django import template
from django.template.defaultfilters import floatformat
from secondary_dashboard.models import Grade
from decimal import Decimal

register = template.Library()

@register.filter
def get_grade(score):
    """Returns the grade based on the score by querying the Grade model."""
    if score is None or score == '':
        return '-'
    
    try:
        score = float(score)
        grade = Grade.objects.filter(min_score__lte=score, max_score__gte=score).first()
        if grade:
            return grade.name
        return '-'
    except (ValueError, TypeError):
        return '-'

@register.filter
def get_grade_color(score):
    """Returns the Bootstrap color class for the grade based on the dynamic grading scheme."""
    if score is None or score == '':
        return 'secondary'

    try:
        score = float(score)
        grade = Grade.objects.filter(min_score__lte=score, max_score__gte=score).first()
        if not grade:
            return 'secondary'

        all_grades = Grade.objects.order_by('grade_point')
        if not all_grades.exists():
            return 'secondary'

        min_points = all_grades.first().grade_point
        max_points = all_grades.last().grade_point
        
        if max_points == min_points:
            return 'success'

        point_range = max_points - min_points
        if point_range == 0:
            return 'success'
        
        percentage = (grade.grade_point - min_points) * 100 / point_range
        
        if percentage >= 75:
            return 'success'
        elif percentage >= 50:
            return 'info'
        elif percentage >= 25:
            return 'warning'
        else:
            return 'danger'

    except (ValueError, TypeError, ZeroDivisionError):
        return 'secondary'


@register.filter
def get_mark(marks, subject_id):
    """Returns the mark for a specific subject."""
    for mark in marks:
         if mark.subject.id == subject_id:
            return mark
    return None

@register.filter
def total_score(marks):
    """Calculates the total score from a queryset of marks."""
    if not marks:
        return 0
    
    valid_scores = [mark.score for mark in marks if mark.score is not None]
    if not valid_scores:
        return 0
    
    return sum(valid_scores)

@register.filter
def average_score(marks):
    """Calculates the average score from a queryset of marks."""
    if not marks:
        return None
    
    valid_scores = [mark.score for mark in marks if mark.score is not None]
    if not valid_scores:
        return None
    
    return sum(valid_scores) / len(valid_scores)

@register.filter
def average_points(marks):
    """Calculates the average points from a queryset of marks using the Grade model."""
    if not marks:
        return None
    
    valid_scores = [mark.score for mark in marks if mark.score is not None]
    if not valid_scores:
        return None
    
    total_points = Decimal('0.0')
    count = 0
    for score in valid_scores:
        try:
            s = float(score)
            grade = Grade.objects.filter(min_score__lte=s, max_score__gte=s).first()
            if grade:
                total_points += grade.grade_point
                count += 1
        except (ValueError, TypeError):
            continue
    
    if count == 0:
        return None

    return floatformat(total_points / Decimal(count), 2)