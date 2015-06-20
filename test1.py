from __future__ import unicode_literals, print_function, generators, division
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_project_.settings")
django.setup()

# ! DJANGO INITED
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.utils.crypto import get_random_string
from photos.models import Photo
from tags.models import Tag, TaggedItem
import random
from datetime import datetime
from django import db
from django.core.cache import caches
from django.contrib.contenttypes.models import ContentType
import csv

cache = caches['default']
User = get_user_model()


def generate_tags(count=100):
    print('generate Tags')
    count_tags = Tag.objects.all().count()
    if count - count_tags <= 0:
        return

    for x in range(count - count_tags):
        try:
            rmd = get_random_string()
            Tag.objects.create(title=rmd, slug=rmd.lower())
        except Exception as e:
            print(e)
    return Tag.objects.values_list('id', flat=True)


def load_photos(tags, data):
    print('load photos')

    ct = ContentType.objects.get_for_model(Photo)
    for index, user_id, url, created in data:
        title = get_random_string()
        tags_num = random.randint(2, 8)
        # p2 = transaction.savepoint()
        try:
            f = Photo.objects.create(id=index, title=title, slug=title.lower(),
                                     url=url, user_id=user_id,
                                     created_at=created)
            while tags_num:
                tag_id = random.choice(tags)
                # p = transaction.savepoint()
                try:
                    _, created = TaggedItem.objects.get_or_create(
                        object_id=f.pk,
                        content_type=ct,
                        tag_id=tag_id)
                    if created:
                        tags_num -= 1
                    # transaction.savepoint_commit(p)
                except IntegrityError:
                    # transaction.savepoint_rollback(p)
                    print(index, 'collision detected', tags_num)
        except IntegrityError as e:
            # transaction.savepoint_rollback(p2)
            print(index, repr(e))


def load_users():
    uniq = set(User.objects.values_list('id', flat=True))
    with open('test-photo.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        for i, row in enumerate(spamreader):
            if i == 0:
                continue
            elif i % 1000 == 0:
                print('processed {0}'.format(i))
            user_id, url, created_at = row
            user_id = int(user_id)
            if user_id in uniq:
                continue

            try:
                rnd = get_random_string()
                User.objects.create(id=user_id, username=rnd)
            except Exception as e:
                print(repr(e))

            uniq.add(user_id)


def load_photo_data(padding=0, max=1000000):
    with open('test-photo.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        c = 0
        for i, row in enumerate(spamreader):
            if i <= padding:
                continue
            elif i % 1000 == 0:
                print(datetime.now().isoformat(), 'processed {0}'.format(i))
            c += 1
            if c > max:
                return
            user_id, url, created_at = row
            user_id = int(user_id)
            created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
            yield (i, user_id, url, created_at)

load_users()
tags = generate_tags()
tags = Tag.objects.values_list('id', flat=True)
data = load_photo_data()
with transaction.atomic():
    load_photos(tags, data)


# for s in db.connection.queries:
#     if float(s['time']) > 0.0001:
#         print(s)
