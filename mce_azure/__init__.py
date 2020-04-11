try:
    from gevent import monkey

    if not monkey.is_module_patched('socket'):
        monkey.patch_all(thread=False)
        import gevent_openssl

        gevent_openssl.monkey_patch()
except ImportError:
    pass
