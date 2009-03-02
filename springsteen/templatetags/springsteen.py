from django import template
register = template.Library()


def clean_url(word, length=75):
    parts = word.split('//')
    if len(parts) > 1:
        word = parts[1]
    if len(word) > length:
        return "%s..." % word[:length-3]
    return word

register.filter('clean_url', clean_url)
