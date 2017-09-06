
from ..env import get_cluster_config
from ..invoke_libs.parse import parse_extra_vars
from functools import wraps
import sys
import os


def with_context(Hook):
    def with_context_decorator(func):
        @wraps(func)
        def outer_func(ctx, datacenter, extra_vars=""):
            try:
                ctx.attributes
            except:
                hook = Hook()
                ev = hook.pre(extra_vars)
                if ev is None:
                    raise Exception("You need to return a string in Hook.pre")
                #attrs = {}
                attrs = parse_extra_vars(ev)
                cluster_config = get_cluster_config(datacenter)
                attrs['cluster_config'] = cluster_config

                ctx.attributes = hook.post(attrs)
                if ctx.attributes is None:
                    raise Exception("You need to return a dictionary in Hook.post")
            return func(ctx, datacenter)
        return outer_func
    return with_context_decorator


class Hook(object):
    def pre(self, extra_vars):
        "hook to modify extra_vars (string)"
        return extra_vars

    def post(self, attrs):
        "hook to modify attrs (dict)"
        return attrs
