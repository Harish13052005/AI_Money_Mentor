import requests, sys
BASE='http://192.168.0.39:8000'
username='mobile_test_user'
email='mobile_test_user@example.com'
password='TestPass123'
print('Registering user...')
r=requests.post(f'{BASE}/register', json={'username':username,'email':email,'password':password})
print('Register status', r.status_code, r.text[:300])
print('Logging in...')
r=requests.post(f'{BASE}/token', data={'username':username,'password':password}, headers={'Content-Type':'application/x-www-form-urlencoded'})
print('Token status', r.status_code, r.text[:300])
if r.status_code!=200:
    print('Auth failed, stop'); sys.exit(1)
access=r.json().get('access_token')
print('Access token length', len(access))
headers={'Authorization':f'Bearer {access}','Content-Type':'application/json'}
print('Posting analyze...')
payload={'income':5000,'expenses':3000,'savings':1000,'investments':[{'type':'stocks','amount':2000}], 'goals':['retirement']}
r=requests.post(f'{BASE}/analyze', json=payload, headers=headers)
print('Analyze', r.status_code, r.text[:800])
print('Getting history...')
r=requests.get(f'{BASE}/history', headers={'Authorization':f'Bearer {access}'})
print('History', r.status_code, r.text[:800])
if r.status_code==200 and r.json():
    rec=r.json()[0]
    rid=rec['id']
    print('Getting record', rid)
    r2=requests.get(f'{BASE}/records/{rid}', headers={'Authorization':f'Bearer {access}'})
    print('Record', r2.status_code, r2.text[:800])
print('Done')
