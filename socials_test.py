from socials import loginVK

s, uid = loginVK()
assert s != None and uid != None
print(f'loginVK()complete! uid: {uid}')