from accounts.models import Teacher

def secondary_teachers(request):
    """
    Hufanya orodha ya walimu wa shule za sekondari ipatikane kwenye
    template zote za secondary_dashboard.
    """
    # Tunachuja walimu ili kupata wale wa 'secondary' pekee
    # na kuwapanga kwa majina yao.
    teachers = Teacher.objects.filter(school_level='secondary').order_by('first_name', 'last_name')
    
    # Tunarudisha dictionary iliyo na orodha ya walimu.
    # 'secondary_teachers' ndilo jina tutakalotumia kwenye template.
    return {'secondary_teachers': teachers}