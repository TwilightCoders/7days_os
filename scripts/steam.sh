#!/usr/local/bin/bash

seven_days_os_pbi_path="/usr/pbi/7days_os-$(uname -m)"

STEAMROOT=${seven_days_os_pbi_path}

STEAMEXE=steamcmd
PLATFORM=linux32

export LD_LIBRARY_PATH="$STEAMROOT/$PLATFORM:$LD_LIBRARY_PATH"

######################################################################
# http://forum.i3d.net/threads/hlds_linux-steamcmd-on-freebsd.184049 #
######################################################################

# PATHLINK=~/.steampath
# rm -f ${PATHLINK} && ln -s ${STEAMROOT}/${PLATFORM}/${STEAMEXE} ${PATHLINK}
# PIDFILE=~/.steampid
# echo $$ > ~/.steampid

# ulimit -n 2048

# # and launch steam
# cd "$STEAMROOT"
# STATUS=42
# while [ $STATUS -eq 42 ]; do
# ${DEBUGGER} "${STEAMROOT}"/${PLATFORM}/${STEAMEXE} "$@"
# STATUS=$?
# done
# exit $STATUS

######################################################################
# https://github.com/Pricetx/Scripts/blob/master/steamcmd_freebsd.sh #
######################################################################

UNAME=`uname`

ulimit -n 2048

MAGIC_RESTART_EXITCODE=42

if [ "$DEBUGGER" == "gdb" ] || [ "$DEBUGGER" == "cgdb" ]; then
    ARGSFILE=$(mktemp $USER.steam.gdb.XXXX)

    # Set the LD_PRELOAD varname in the debugger, and unset the global version.
    if [ "$LD_PRELOAD" ]; then
        echo set env LD_PRELOAD=$LD_PRELOAD >> "$ARGSFILE"
        echo show env LD_PRELOAD >> "$ARGSFILE"
        unset LD_PRELOAD
    fi

    $DEBUGGER -x "$ARGSFILE" "$STEAMROOT/$PLATFORM/$STEAMEXE" "$@"
    rm "$ARGSFILE"
else
    $DEBUGGER "$STEAMROOT/$PLATFORM/$STEAMEXE" "$@"
fi

STATUS=$?

if [ $STATUS -eq $MAGIC_RESTART_EXITCODE ]; then
    exec "$0" "$@"
fi
exit $STATUS
