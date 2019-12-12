import redis,time

r = redis.Redis(charset='utf-8',decode_responses=True)

r.set('mobile','123')
r.expire('mobile',1)  # 设置mobile在1秒后过期
time.sleep(1)
print(r.get('mobile'))