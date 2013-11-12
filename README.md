[![Build Status](https://travis-ci.org/ImmaculateObsession/nest.png?branch=master)](https://travis-ci.org/ImmaculateObsession/nest)

NEST

To run Nest:
 
- clone the repo (git clone....)
- create a virtualenv in the repo directory (cd nest && virtualenv .)
- activate virtualenv (. bin/activate)
- install requirements (pip install -r requirements/base.txt)
- create nest db (python manage.py syncdb --settings=nest.settings.base)
- load test data (python manage.py loaddata comics.json --settings=nest.settings.base)
- run nest dev server (python manage.py runserver --settings=nest.settings.base)

Share and enjoy.

NOTE: Do not use bootstrap's glyphicons. Use the icons from Font Awesome.