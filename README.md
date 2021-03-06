[![Build Status](https://travis-ci.org/ImmaculateObsession/nest.png?branch=master)](https://travis-ci.org/ImmaculateObsession/nest)

1. Install virtualbox (https://www.virtualbox.org/)
2. Pull the 'nest' repo (nest is the name of the project on github)
3. cd into the repo and run 'vagrant up'. This should build and start your dev environment
4. When it has completed, run 'vagrant ssh'. This will log you into your dev environment
5. Type 'rs' to run the dev server, which will be available on your host machine at localhost:8000

A common workflow looks like this:

1. Pull changes from git ('git pull --rebase')
2. Make any changes you need to the codebase on your host machine
3. Test against your dev server
4. Commit your changes
5. Check for new changes from git ('git pull --rebase')
6. Push your changes to git ('git push origin master')

NOTE: Do not use bootstrap's glyphicons. Use the icons from Font Awesome.