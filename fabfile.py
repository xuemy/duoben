#!/usr/bin/python
# -*- coding: utf-8 -*-
from fabtools.require.nginx import enabled
import os
import posixpath
from fabric.colors import red, green
from fabric.api import *

import fabtools
from fabtools import require
from fabtools.vagrant import vagrant, vagrant_settings

current_dir = posixpath.dirname(posixpath.abspath(__file__))

# 设置一些变量
host_ip = "104.237.159.20"
host_port = 22

git_url = "https://xuemy@bitbucket.org/xuemy/wumingshu.git"

proxy_port = 8889
proxy_url = "'http://127.0.0.1:%s'" % proxy_port

log_dir = lambda home: posixpath.join(home, "log")

gunicorn_log_dir = lambda home: posixpath.join(log_dir(home), "gunicorn")
'''
拿到一个vps后第一次运行 first() 函数,安装一些ubuntu必须的包，创建一个具有 sudo 权限的用户
'''

# # root_host = "%s@%s:%s" % (root, host_ip, host_port)
# user_host = "%s@%s:%s" % (user, host_ip, host_port)
#
# env.roledefs = {
# # "root": [root_host],
# "user": [user_host],
#     }
# env.passwords = {
#     # root_host:root_pw,
#     user_host:user_pw
# }

# 第一步 执行这个

@task
def root():
    env.user = "root"
    env.password = ""


@task
def user():
    env.user = "duoben"
    env.password = "duoben"
    env.mysql_root = "root"
    env.mysql_root_pw = "xmy@5650268"
    env.mysql_user = env.user
    env.mysql_db = env.user
    env.mysql_pw = "xmy@5650268"

    home = fabtools.user.home_directory(env.user)
    env.virtualenv_dir = posixpath.join(home, "virtuanenv")
    env.code_dir = posixpath.join(home, "%s_code" % env.user)
    media_dir = posixpath.join(env.code_dir, "media")
    env.static_dir = posixpath.join(env.code_dir, "static")
    env.log_dir = posixpath.join(home, "log")

    # 确保文件存在
    require.directory(env.media_dir)
    require.directory(env.log_dir)


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
    require.users.user(env.user, password=env.password, shell="/bin/bash")
    require.users.sudoer(env.user)


@task
def first():
    execute(install_deb)
    execute(add_user)


@task
def create_mysql():
    require.mysql.server(password=env.mysql_root_pw)
    with settings(mysql_user=env.mysql_root, mysql_password=env.mysql_root_pw):
        require.mysql.user(env.mysql_user, env.mysql_pw)
        require.mysql.database(env.mysql_db, owner=env.mysql_user)


@task
@roles("user")
def create_nginx():
    home = fabtools.user.home_directory(user)
    require.nginx.server()
    PROXIED_SITE_TEMPLATE = """\
server {
    listen %(port)s default;
    server_name www.ydzww.com ydzww.com;
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

    if ($host = 'ydzww.com' ){
        rewrite ^/(.*)$ http://www.ydzww.com/$1 permanent;
    }

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
        proxy_pass %(proxy_url)s;
    }

    access_log /var/log/nginx/%(user)s.log;
}
"""
    require.nginx.site('one.com', template_contents=PROXIED_SITE_TEMPLATE,
                       enabled=True,
                       docroot=home,
                       proxy_url=proxy_url,
                       media_dir=media_dir(home),
                       static_dir=static_dir(home),
                       user=user
    )


def git_clone():
    puts(red("从git中 clone代码"))
    home = fabtools.user.home_directory(user)
    fabtools.git.clone(git_url, code_dir(home))
    puts(red("从git clone完成"))


@roles("user")
@task
def config_django():
    home = fabtools.user.home_directory(user)
    with cd(code_dir(home)):
        with fabtools.python.virtualenv(virtualenv_dir(home)):
            run("python manage.py syncdb")
            run("python manage.py makemigrations")
            run("python manage.py migrate")
            run("python manage.py loaddata data.json")


@task
@roles("user")
def update_database():
    home = fabtools.user.home_directory(user)
    with cd(code_dir(home)):
        with fabtools.python.virtualenv(virtualenv_dir(home)):
            run("python manage.py makemigrations")
            run("python manage.py migrate")


@task
@roles("user")
def collection_static():
    home = fabtools.user.home_directory(user)
    with cd(code_dir(home)):
        with fabtools.python.virtualenv(virtualenv_dir(home)):
            run("python manage.py collectstatic")


@task
@roles("user")
def add_local_settings():
    puts(red("添加local_settings"))
    home = fabtools.user.home_directory(user)
    setting_file = posixpath.join(code_dir(home), "shu", "local_settings.py")
    setting_template = '''\
#encoding:utf-8
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DEBUG = False
ALLOWED_HOSTS = ["ydzww.com","www.ydzww.com","104.237.159.20"]
TEMPLATE_DEBUG = False
DB_NAME = "%(db_name)s"
DB_USER = "%(db_user)s"
DB_PASSWORD = "%(db_pw)s"
STATIC_ROOT = "%(static_dir)s"
MEDIA_ROOT = "%(media_dir)s"
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR,"cache"),
        'TIMEOUT': 60,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

'''
    require.files.template_file(setting_file, template_contents=setting_template, context=dict(
        db_name=mysql_db, db_user=mysql_user, db_pw=mysql_pw, static_dir=static_dir(home),
        media_dir=media_dir(home))
    )
    puts(green("添加local_settings完成"))


@task
def install_virtualenv():
    home = fabtools.user.home_directory(user)
    # 创建virtualenv
    require.python.virtualenv(virtualenv_dir(home))

    with fabtools.python.virtualenv(virtualenv_dir(home)):
        fabtools.python.install(["django",
                                 "gunicorn",
                                 "django-codemirror-widget",
                                 "django-jsonfield",
                                 "pillow",
                                 "scrapy",
                                 "MySQL-python",
                                 "gevent"])


@task
def install_gunicorn():
    home = fabtools.user.home_directory(user)
    _virtualenv_dir = virtualenv_dir(home)
    gunicorn_command = posixpath.join(_virtualenv_dir, "bin/gunicorn")

    access_log = posixpath.join(gunicorn_log_dir(home), "access.log")
    error_log = posixpath.join(gunicorn_log_dir(home), "error.log")
    require.files.file(access_log)
    require.files.file(error_log)

    supervisor_log = posixpath.join(log_dir(home), "supervisor.log")
    require.files.file(supervisor_log)

    require.supervisor.process(user,
                               command='%(gunicorn_command)s shu.wsgi:application -w 4 -b :%(proxy_port)s -k gevent --max-requests 500 --access-logfile=%(access_log)s --error-logfile=%(error_log)s' %
                                       dict(gunicorn_command=gunicorn_command,
                                            access_log=access_log,
                                            error_log=error_log,
                                            proxy_port=proxy_port),
                               directory=code_dir(home),
                               user=user,
                               process_name=user,
                               stdot_logfile=supervisor_log)


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


@roles("user")
@task
def git_pull():
    home = fabtools.user.home_directory(user)
    fabtools.git.pull(code_dir(home))


@task
@roles("user")
def restart_web():
    fabtools.supervisor.restart_process(user)


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