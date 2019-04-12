#!/usr/bin/env bash

set -ex

if [[ "$(uname -s)" == 'Darwin' ]]; then
    brew update || brew update
    brew outdated pyenv || brew upgrade pyenv
    brew install pyenv-virtualenv
    
    if ! type "cmake" > /dev/null; then
        brew install cmake
    else
        brew upgrade cmake
    fi

    if which pyenv > /dev/null; then
        eval "$(pyenv init -)"
    fi

    export LDFLAGS="${LDFLAGS} -L/usr/local/opt/zlib/lib"
    export CPPFLAGS="${CPPFLAGS} -I/usr/local/opt/zlib/include"
    export PKG_CONFIG_PATH="${PKG_CONFIG_PATH} /usr/local/opt/zlib/lib/pkgconfig"
    
    pyenv install 3.7.1
    pyenv virtualenv 3.7.1 conan
    pyenv rehash
    pyenv activate conan
fi

pip install conan --upgrade
pip install conan_package_tools bincrafters_package_tools

conan user