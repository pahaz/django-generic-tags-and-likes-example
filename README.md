# Simple Tagged/Liked Photo Server

Example of use django generic models (contenttype framework). Provide two 
generic apps: `tags` and `likes`. And `photos` app as example of use `tags` and
 `likes`.

Required Django 1.8!

    class Photo(LikedModel, TaggedModel, Owned, Slugged, Dated):
        url = models.URLField(verbose_name=_("Photo URL"))
        
        class Meta:
            db_table = "photo"
            verbose_name = _("Photo")
            verbose_name_plural = _("Photos")

## LikedModel ##

Abstract Interface:

 - `objects_liked_by(user)`
 - `like_by(user)`
 - `dislike_by(user)`
 - `is_liked_by(user)`
 - `likes`  # get property

## TaggedModel ##

Abstract Interface:

 - `objects_tagged_by_any(tags, exclude_tags)`
 - `objects_tagged_by_all(tags, exclude_tags)`
 - `tags`  # get/set property

# How-To

    # install MySQL/MariaDb (if you want)
    git clone https://github.com/Lukx/vagrant-lamp.git
    cd vagrant-lamp
    vagrant up
    
    # port forward to MySQL/MariaDb (if use vagrant and MySQL/MariaDb)
    easy_install pycrypto
    easy_install sshtunnel
    python -m sshtunnel -U vagrant -P vagrant -L :3306 -R 127.0.0.1:3306 -p 2222 localhost
    
    # init project __data__ (venv, cache, media)
    python init.py
    
    # activate venv
    __data__\venv\Scripts\activate  # windows
    __data__\venv\bin\activate  # unix
    
    python runtests.py  # (if you want)
    
    # generate test-photo.csv file .. (fileformat: "user_id";"src";"created_at")
    python test1.py  # fill database data
    
    python manage.py migrate
    python manage.py runserver
