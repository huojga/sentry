"""
sentry.runner.decorators
~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2015 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import, print_function

import os

from click import Choice

LOG_LEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'FATAL')


class CaseInsensitiveChoice(Choice):
    def convert(self, value, param, ctx):
        return super(CaseInsensitiveChoice, self).convert(value.upper(), param, ctx)


def configuration(f):
    "Load and configure Sentry."
    import click
    from functools import update_wrapper

    @click.pass_context
    def inner(ctx, *args, **kwargs):
        # HACK: We can't call `configure()` from within tests
        # since we don't load config files from disk, so we
        # need a way to bypass this initialization step
        if os.environ.get('_SENTRY_SKIP_CONFIGURATION') != '1':
            from sentry.runner import configure
            configure()
        return ctx.invoke(f, *args, **kwargs)
    return update_wrapper(inner, f)


def log_level_option(f):
    "Give ability to configure global logging level. Must be used before configuration."
    import click
    from functools import update_wrapper

    @click.pass_context
    @click.option('--loglevel', '-l', default=None,
        help='Global logging level. Use wisely.',
        envvar='SENTRY_LOG_LEVEL',
        type=CaseInsensitiveChoice(LOG_LEVELS))
    def inner(ctx, *args, **kwargs):
        level = kwargs.pop('loglevel', None)
        if level:
            from os import environ
            environ['SENTRY_LOG_LEVEL'] = level
        return ctx.invoke(f, *args, **kwargs)
    return update_wrapper(inner, f)
