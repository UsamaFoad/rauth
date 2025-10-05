#!/bin/sh

OUTPUT_PATH=`pwd`/tests_output

log()
{
    echo "$@" | tee -a $OUTPUT_PATH/test.log
}

pytest_cov_plugin()
{
    python -c "import pytest_cov" 2>/dev/null
}

pytest_color_support()
{
    python -c "import pytest" 2>/dev/null
}

rm -rf $OUTPUT_PATH
mkdir -p $OUTPUT_PATH

if [ -n "$VERBOSE" ]; then
    PYTEST_OPTIONS="$PYTEST_OPTIONS -v"
fi

if [ -z "$NOCOLOR" ] && pytest_color_support; then
    PYTEST_OPTIONS="$PYTEST_OPTIONS --color=yes"
fi

if [ -n "$OPTIONS" ]; then
    PYTEST_OPTIONS="$PYTEST_OPTIONS $OPTIONS"
fi

if [ -n "$TESTS" ]; then
    PYTEST_OPTIONS="$PYTEST_OPTIONS $TESTS"
else
    PYTEST_OPTIONS="$PYTEST_OPTIONS --cov=rauth --cov-report=term-missing --cov-fail-under=100"
fi

log "Running tests..."

if [ $BASH ]; then
    pytest $PYTEST_OPTIONS 2>&1 | tee -a $OUTPUT_PATH/test.log
    R=${PIPESTATUS[0]}
else
    4>&1 R=$({ { pytest $PYTEST_OPTIONS 2>&1; echo $? >&3 ; } | { tee -a $OUTPUT_PATH/test.log >&4; } } 3>&1)
fi

echo

pytest --version
python -V

case "$R" in
    0) log "SUCCESS" ;;
    *) log "FAILURE" ;;
esac

exit $R
