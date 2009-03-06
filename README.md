# django-springsteen


## Normal Installation

1.  Fetch repository from GitHub.

        git clone git://github.com/lethain/django-springsteen.git

2. Add to Python path.

        cd git/django-springsteen/
        ln -s `pwd`/springsteen /Library/Python/2.5/site-packages/springsteen

3.  Go to ``example_project`` directory.

        cd example_project

4.  Create a ``boss_settings.py`` file which contains the
    variables specified in ``Configuration Settings`` section.

5.  Run development server.

        python manage.py runserver

### Google App Engine Installation

1.  Fetch repository from GitHub.

        git clone git://github.com/lethain/django-springsteen.git

2.  Run the ``pack_for_gae.sh`` script.

        chmod +x ./scripts/pack_for_gae.sh
        ./scripts/pack_for_gae

2.  Move into the ``gae`` directory.

        cd gae

3.  Open up ``app.yaml`` and replace ``djangosearch``
    in the first line with the name of your application.

4.  Create a ``boss_settings.py`` file which contains the
    variables specified in ``Configuration Settings`` section.

5.  Run the GAE Development Server.

        cd gae
        dev_appserver.py ./

## Configuration Settings

* ``BOSS_APP_ID`` is your BOSS App ID assigned by Yahoo!
* ``SPRINGSTEEN_LOG_QUERIES`` specifies whether or not to log queries.
* ``SPRINGSTEEN_LOG_DIR`` is the directory to create the ``queries.log``
    file that contains logged queries.
