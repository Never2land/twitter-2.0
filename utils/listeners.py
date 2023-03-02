def invalidate_object_cache(sender, instance, **kwargs):
    from utils.memcached_helper import MemchachedHelper

    MemchachedHelper.invalidate_object_cache(sender, instance.id)
