from moderation.models import ExceptionWord, ObsceneWord
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def highlight_words(value):
    bad_words = [word.word for word in ObsceneWord.objects.all()]
    exceptions = [word.word for word in ExceptionWord.objects.all()]
    words = value.split()

    highlighted_text = ""

    for word in words:
        if word.lower() in bad_words and word.lower() not in exceptions:
            highlighted_text += f'<span style="color: red">{word}</span> '
        elif word.lower() not in exceptions:
            bad = False
            for bad_word in bad_words:
                if bad_word in word.lower():
                    highlighted_text += f'<span style="color: red">{word}</span> '
                    bad = True
                    break
            if not bad:
                highlighted_text += f"{word} "
        else:
            highlighted_text += f"{word} "

    return mark_safe(highlighted_text)
