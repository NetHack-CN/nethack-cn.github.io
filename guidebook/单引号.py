o = open('guidebook366-zh.mn', 'r', encoding='utf-8').read()
d = ''
for i in range(len(o)):
	if o[i] == '“' and o[i + 2] == '”':
		d += '‘'
		continue
	if o[i - 2] == '“' and o[i] == '”':
		d += '’'
		continue
	d += o[i]
with open('guidebook366-buf.html', 'w', encoding='utf-8') as f:
	f.write(d)