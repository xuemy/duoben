#!/usr/bin/python
# -*- coding: utf-8 -*-
from fabtools.require.nginx import enabled
import posixpath
from fabric.colors import red, green
from fabric.api import *

import fabtools
from fabtools import require
from fabtools.vagrant import vagrant, vagrant_settings

current_dir = posixpath.dirname(posixpath.abspath(__file__))

PROXIED_SITE_TEMPLATE = """\
upstream app_server {
        server unix:%(bind)s fail_timeout=0;
    }
server {
    listen %(port)s default;
    server_name -;
    default_type application/octet-stream;
    gzip on;
    gzip_http_version 1.0;
    gzip_proxied any;
    gzip_min_length 500;
    gzip_disable "MSIE [1-6]\.";
    gzip_types text/plain text/html text/xml text/css
                text/comma-separated-values
                text/javascript application/x-javascript
                application/atom+xml image/jpeg image/gif image/png;

    # root /home/one;



    location /static/ {
        alias %(static_dir)s/;


    }

    location /media/ {
        alias %(media_dir)s/;
        expires 30d;
    }

    location / {
        try_files $uri @proxied;
    }

    location @proxied {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_pass http://app_server;
    }

    access_log %(nginx_log)s/access.log;
}
"""


# 第一步 执行这个

@task
def root():
    env.user = "root"
    env.password = ""

env.hosts = ["127.0.0.1"]
@task
def user():

    env.port = 2222
    env.user = "duoben"
    env.password = "duoben"

    env.mysql_root_pw = "xmy@5650268"

    env.mysql_user = "duoben"
    env.mysql_pw = "xmy@5650268"

    env.mysql_db = "duoben"

    env.git = "https://github.com/xuemy/duoben.git"

    home = fabtools.user.home_directory(env.user)

    env.virtualenv_dir = posixpath.join(home, "virtuanenv")
    env.code_dir = posixpath.join(home, "%s_code" % env.user)

    env.media_dir = posixpath.join(env.code_dir, "media")
    env.static_dir = posixpath.join(env.code_dir, "static")
    env.log_dir = posixpath.join(home, "log")
    env.nginx_log = posixpath.join(env.log_dir, "nginx")

    env.bind = posixpath.join(home, "gunicorn.sock")

    # 确保文件存在

    require.directory(env.log_dir)
    require.directory(env.nginx_log)


def install_deb():
    require.deb.packages([
        "python-dev",
        "python-lxml",
        "python-imaging",
        "git",
        "libffi-dev",
        "libxml2",
        "python-libxslt1",
        "python-libxml2",
        "libxslt1-dev",
        "libxml2-dev",
        "libmysqlclient-dev",
        "libjpeg-dev",
        "libfreetype6-dev"
    ])


@task
def add_user():
    # create sudoer user
    require.users.user("duoben", password="duoben", shell="/bin/bash")
    require.users.sudoer("duoben")


@task
def first():
    execute(install_deb)
    execute(add_user)


@task
def create_mysql():
    require.mysql.server(password=env.mysql_root_pw)
    with settings(mysql_user="root", mysql_password=env.mysql_root_pw):
        puts(red("设置mysql user"))
        require.mysql.user("duoben", "xmy@5650268")
        require.mysql.database("duoben", owner="duoben")


@task
def create_nginx():
    require.nginx.server()
    domain = "duoben.com"

    require.nginx.site(domain,
                       template_contents=PROXIED_SITE_TEMPLATE,
                       port = 80,
                       bind = env.bind,
                       media_dir = env.media_dir,
                       static_dir = env.static_dir,
                       nginx_log = env.nginx_log
    )

@task
def git_clone():
    puts(red("从git中 clone代码"))
    fabtools.git.clone(env.git,env.code_dir)
    puts(red("从git clone完成"))
    require.directory(env.media_dir)


@task
def git_pull():
    fabtools.git.pull(env.code_dir)


@task
def install_virtualenv():
    # 创建virtualenv
    require.python.virtualenv(env.virtualenv_dir)

    with fabtools.python.virtualenv(env.virtualenv_dir):
        fabtools.python.install(["django",
                                 "gunicorn",
                                 "django-codemirror-widget",
                                 "django-jsonfield",
                                 "pillow",
                                 "scrapy",
                                 "MySQL-python",
                                 "gevent",
                                 "pypinyin"]
        )


@task
def config_settings():
    puts(red("添加local_settings"))
    setting_file = posixpath.join(env.code_dir, "duoben", "local_settings.py")
    setting_template = '''\
#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib import admin
from django.conf.urls import patterns, url, include
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_NAME = "duoben"
DB_USER = "duoben"
DB_PASSWORD = "xmy@5650268"

local_url = patterns("",url(r'^xmy/admin/', include(admin.site.urls)),)
ALLOWED_HOSTS = ["*"]

STATIC_ROOT = os.path.join(BASE_DIR, "static")

DEBUG = True
TEMPLATE_DEBUG = True
if DEBUG:
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,

            }
    }

'''
    require.files.template_file(setting_file,
                                template_contents=setting_template,
                                context=dict(db_name=env.mysql_db,db_user=env.mysql_user,db_passwd=env.mysql_pw)
    )
    puts(green("添加local_settings完成"))


@task
def config_django():
    with cd(env.code_dir):
        with fabtools.python.virtualenv(env.virtualenv_dir):
            run("python manage.py syncdb")
            run("python manage.py makemigrations")
            run("python manage.py migrate")

@task
def config_staticfile():
    with cd(env.code_dir):
        with fabtools.python.virtualenv(env.virtualenv_dir):
            run("python manage.py collectstatic")



@task
def install_gunicorn():
    gunicorn_command = posixpath.join(env.virtualenv_dir, "bin/gunicorn")
    access_log = posixpath.join(env.log_dir, "access.log")
    error_log = posixpath.join(env.log_dir, "error.log")
    require.files.file(access_log)
    require.files.file(error_log)

    supervisor_log = posixpath.join(env.log_dir, "supervisor.log")
    require.files.file(supervisor_log)

    require.supervisor.process(env.user,
                               command='%(gunicorn_command)s duoben.wsgi:application '
                                       '-w 4 -b unix:%(bind)s '
                                       '-k gevent --max-requests 500 '
                                       '--access-logfile=%(access_log)s '
                                       '--error-logfile=%(error_log)s ' %

                                       dict(gunicorn_command=gunicorn_command,
                                            access_log=access_log,
                                            error_log=error_log,
                                            bind=env.bind),
                               directory=env.code_dir,
                               user="duoben",
                               process_name=env.user,
                               stdout_logfile=supervisor_log)






@task
@roles("user")
def update_database():
    home = fabtools.user.home_directory(user)
    with cd(code_dir(home)):
        with fabtools.python.virtualenv(virtualenv_dir(home)):
            run("python manage.py makemigrations")
            run("python manage.py migrate")




@roles("user")
@task
def config_crawl():
    home = fabtools.user.home_directory(user)
    crawl_name = "crawl_shu"
    crawl_path = posixpath.join(home, crawl_name + ".sh")
    crawl_log = posixpath.join(log_dir(home), "crawl.log")
    require.files.file(crawl_log)
    template = '''\
#!/bin/bash

cd %(virtualenv_scrapy)s
source activate
cd %(crawl)s
while true
do
    scrapy crawl shu --logfile=%(crawl_log)s
    sleep 240
done
''' % dict(crawl=posixpath.join(code_dir(home), "crawl"),
           scrapy_bin=posixpath.join(virtualenv_dir(home), "bin", "scrapy"),
           virtualenv_scrapy=posixpath.join(virtualenv_dir(home), 'bin'),
           crawl_log=crawl_log)
    require.files.file(crawl_path, contents=template)
    require.supervisor.process(crawl_name,
                               command="/bin/bash %s" % crawl_path,
                               directory=posixpath.join(code_dir(home), "crawl"),
                               user=user,
                               process_name=crawl_name,
    )




@task
def restart_web():
    fabtools.supervisor.restart_process(env.user)


@task
@roles("user")
def start_web():
    fabtools.supervisor.start_process(user)


@roles("user")
@task
def second():
    # 创建一个 数据库
    # puts(red("开始创建数据库"))
    # create_mysql()
    # puts(green("创建数据库成功"))

    # puts(red("开始创建 Media 、log文件夹"))
    # create_files()
    # puts(green("创建文件夹成功"))

    # install_virtualenv()
    # git_clone()
    # add_local_settings()
    config_django()
    collection_static()

    install_gunicorn()
    create_nginx()


@task
@roles("user")
def test():
    home = fabtools.user.home_directory(user)
    # with cd(code_dir(home)):
    #     with fabtools.python.virtualenv(virtualenv_dir(home)):
    #         run("python manage.py loaddata data.json")
    with fabtools.python.virtualenv(virtualenv_dir(home)):
        with cd(posixpath.join(code_dir(home), "crawl")):
            run("scrapy crawl shu")


@task
@roles("user")
def crawl():
    crawl_template = '''\
#!/bin/bash

cd %(virtualenv_dir)s
source ./bin/activate
cd %(crawl_dir)s
while true
do
    scrapy crawl %(crawl_name)s --logfile=%(crawl_log)s
    sleep %(sleep_time)s
done
'''
    home = fabtools.user.home_directory(user)
    crawl_dir = posixpath.join(code_dir(home), "crawl")
    virtualenv_ = posixpath.join(home, "virtualenv")

    def custom_crawl(crawl_name):
        crawl_sh = posixpath.join(home, crawl_name)
        require.files.file(path=crawl_sh, contents=crawl_template % dict(
            virtualenv_dir=virtualenv_,
            crawl_dir=crawl_dir,
            crawl_name=crawl_name,
            crawl_log=posixpath.join(log_dir(home), "%s.log" % crawl_name),
            sleep_time=180
        ))

        require.supervisor.process(crawl_name,
                                   command="/bin/bash %s" % crawl_sh,
                                   directory=posixpath.join(code_dir(home), "crawl"),
                                   user=user,
                                   process_name=crawl_name, )

    # main crawl
    custom_crawl("main_crawl")
    custom_crawl("single_crawl")
    custom_crawl("hot_crawl")


@task
@roles("user")
def stop_crawl():
    fabtools.supervisor.stop_process("main_crawl")
    fabtools.supervisor.stop_process("single_crawl")
    fabtools.supervisor.stop_process("hot_crawl")


@task
@roles("user")
def start_crawl():
    fabtools.supervisor.start_process("main_crawl")
    fabtools.supervisor.start_process("single_crawl")
    fabtools.supervisor.start_process("hot_crawl")