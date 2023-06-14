from logging import Logger

from redis import Redis

from src.my_redis.inmemory_redis import InmemoryRedis


def setup_redis(
    debug: str | None, error_logger: Logger,
    main_logger: Logger, redis_host: str, redis_port: str
  ) -> Redis:
  if debug:
      r = InmemoryRedis(redis_host, int(redis_port))
  else:
      r = Redis(redis_host, int(redis_port))
      try:
          if r.ping():
              main_logger.info("Redis is ready")
      except Exception as e:
          error_logger.error(e)
          main_logger.error("Redis is not ready")
          raise e
  return r
