o = open('guidebook366-zh.mn', 'r', encoding='utf-8').read()
d = ''
for i in range(len(o)):
	if o[i] == '“' and o[i + 2] == '”':
		d += '‘'
		continue
	if o[i - 2] == '“' and o[i] == '”':
		d += '’'
		continue
	if o[i] == '“' and o[i + 1] == '^' and o[i + 3] == '”':
		d += '‘'
		continue
	if o[i - 3] == '“' and o[i - 2] == '^' and o[i] == '”':
		d += '’'
		continue
	d += o[i]
print(d)
with open('Guidebook366-zh.mn', 'w', encoding='utf-8') as f:
	f.write(d)