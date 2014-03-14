# if running bash
if [ -n "$BASH_VERSION" ]; then
    # include .bashrc if it exists
    if [ -f "$HOME/.bashrc" ]; then
        . "$HOME/.bashrc"
    fi
fi

# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/bin" ] ; then
    PATH="$HOME/bin:$PATH"
fi

function djmanages {
    pushd /home/vagrant/nest
    python manage.py $@
    popd
}

function ipgrunt {
    pushd /home/vagrant/nest/static
    grunt
    popd
}

. ip/bin/activate
export SECRET_KEY=123456789
export MANDRILL_KEY=123456789
alias rs="djmanages runserver 0.0.0.0:8000 --settings=nest.settings.base"
alias nest-cover="coverage run --source='comics,pebbles,profiles,saltpeter,nest' --omit='*migrations*,*tests*,*settings*,*urls*,*wsgi*' manage.py test comics pebbles profiles saltpeter nest --settings=nest.settings.base && coverage report"
[[ -s $HOME/.nvm/nvm.sh ]] && . $HOME/.nvm/nvm.sh # This loads NVM
nvm use 0.10