import pathlib
files=[
    'api-gateway/main.py',
    'guest-service/main.py',
    'room-service/main.py',
    'booking-service/main.py',
    'payment-service/main.py',
    'staff-service/main.py',
    'feedback-service/main.py',
]
for f in files:
    p=pathlib.Path(f)
    if not p.exists():
        print('missing',f)
        continue
    txt=p.read_text(encoding='utf-8')
    if 'from fastapi.middleware.cors import CORSMiddleware' in txt:
        print(f,'already has CORS')
        continue
    if 'from fastapi import ' in txt:
        lines=txt.splitlines()
        for i,l in enumerate(lines):
            if l.startswith('from fastapi import '):
                lines.insert(i+1,'from fastapi.middleware.cors import CORSMiddleware')
                break
        txt='\n'.join(lines)
    app_pos=txt.find('app = FastAPI(')
    if app_pos!=-1:
        pos=txt.find('\n\n',app_pos)
        if pos!=-1:
            insert='\napp.add_middleware(\n    CORSMiddleware,\n    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://localhost:3004", "http://localhost:3005", "http://localhost:3006", "http://localhost:8000"],\n    allow_credentials=True,\n    allow_methods=["*"],\n    allow_headers=["*"],\n)\n'
            txt=txt[:pos]+insert+txt[pos:]
        else:
            print(f,'could not find insertion point for app block')
            continue
    else:
        print(f,'no FastAPI app found')
        continue
    p.write_text(txt,encoding='utf-8')
    print(f,'updated with CORS')
