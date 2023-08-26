#!/bin/bash

# Fail on errors.
set -e

# Make sure .bashrc is sourced
. /root/.bashrc

# Allow the workdir to be set using an env var.
# Useful for CI pipiles which use docker for their build steps
# and don't allow that much flexibility to mount volumes
WORKDIR=${SRCDIR:-/src}

#
# In case the user specified a custom URL for PYPI, then use
# that one, instead of the default one.
#
if [[ "$PYPI_URL" != "https://pypi.python.org/" ]] || \
   [[ "$PYPI_INDEX_URL" != "https://pypi.python.org/simple" ]]; then
    # the funky looking regexp just extracts the hostname, excluding port
    # to be used as a trusted-host.
    mkdir -p /wine/drive_c/users/root/pip
    echo "[global]" > /wine/drive_c/users/root/pip/pip.ini
    echo "index = $PYPI_URL" >> /wine/drive_c/users/root/pip/pip.ini
    echo "index-url = $PYPI_INDEX_URL" >> /wine/drive_c/users/root/pip/pip.ini
    echo "trusted-host = $(echo $PYPI_URL | perl -pe 's|^.*?://(.*?)(:.*?)?/.*$|$1|')" >> /wine/drive_c/users/root/pip/pip.ini

    echo "Using custom pip.ini: "
    cat /wine/drive_c/users/root/pip/pip.ini
fi

cd $WORKDIR

echo "$@"

if [[ "$@" == "" ]]; then
    if [ -f requirements.txt ]; then
        # use --no-cache-dir to try to reduce memory usage. (see https://github.com/pypa/pip/issues/2984)
        pip install --no-cache-dir -r requirements.txt
    fi # [ -f requirements.txt ]

    if [ -f "./builder/prepare.sh" ]; then
        echo "running builder/prepare.sh"
        chmod +x "./builder/prepare.sh"
        "./builder/prepare.sh"
    else
        echo "No prepare.sh"
    fi # [ -f "./builder/prepare.sh" ]

    pyinstaller --clean -y --dist ./dist/windows --workpath /tmp *.spec
    chown -R --reference=. ./dist/windows
else
    sh -c "$@"
fi # [[ "$@" == "" ]]
