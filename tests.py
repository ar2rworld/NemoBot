#I have no idea how to test python but i need this function to be tested
#import make_post from socials
from src.socialsInteractions.socials import dec

try:
  params = 'a=1&b=123&c=a1@><)- 1_'
  res = dec(params)
  assert res['a'] == '1', 'missing value "a"'
  assert res['b'] == '123', 'missing value "b"'
  assert res['c'] == 'a1@><)- 1_', 'missing value "c"'
  print(f'Success with dec()!')
except Exception as e:
  print(f'Error with dec():\n{e}')

#testing make_post
'''
try:
  make_post()
  
except Exception as e:
  print(f'Something went wrong:\n{e}')
'''