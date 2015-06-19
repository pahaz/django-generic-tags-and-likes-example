from __future__ import unicode_literals, print_function, generators, division
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _

__author__ = 'pahaz'
# based on django-tagging/tagging/utils.py


def parse_tag_input(input):
    """
    Parses tag input, with multiple word input being activated and
    delineated by commas and double quotes. Quotes take precedence, so
    they may contain commas.
    Returns a sorted list of unique tag names.
    """
    if not input:
        return []

    input = force_text(input)
    has_quote = '"' in input or "'" in input

    if not has_quote:
        words = split_strip(input, ',')
    else:
        # TODO: more flexible parsing
        raise NotImplementedError
    return only_unique(words)


def join_tags(tags):
    if not tags:
        return ""

    has_comma_in_any_tag = any(map(lambda x: ',' in x, tags))
    if has_comma_in_any_tag:
        # TODO: more flexible joining
        raise NotImplementedError
    return ', '.join(tags)


def split_strip(input, delimiter=','):
    """
    Splits ``input`` on ``delimiter``, stripping each resulting string
    and returning a list of non-empty strings.
    """
    if not input:
        return []

    words = [w.strip() for w in input.split(delimiter)]
    return [w for w in words if w]


def only_unique(words):
    added_words = set()
    result = []
    for word in words:
        if word in added_words:
            continue
        added_words.add(word)
        result.append(word)
    return result
