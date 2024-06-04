from django.core.cache import cache

class Redis:
    def __init__(self, expiry):
        self.expiry = expiry

    def get(self, key):
        return cache.get(key)
    
    def set(self, key, value):
        cache.set(key, value, self.expiry)


    def hset(self, hash, key, value, expiry):
        hash_dict = cache.get(hash)
        if cache.get(hash) is None:
            hash_dict = {
                key: value
            }
        else:
            hash_dict[key] = value
        cache.set(hash, hash_dict, expiry)

    def hget(self, hash, key):
        try:
            return cache.get(hash)[key]
        except:
            return None


redisInstance = Redis(10)

