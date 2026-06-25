'''
フランキウム-223：谁要是看到了这段代码，来救救我吧……如果有更好的解决方法的话。
在我岂不是毫无帮助吗？智慧岂不是从我心中赶出净尽吗？ 
2026.06.24（今夕何夕）
'''
import re
mn = open('./Guidebook366-zh.mn', 'r', encoding='utf-8').readlines()
latin = 'qwertyuioppasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
out = ''
WIDTH = 75
center = []
box = []
cen = False
boks = False
hn = [0, 0, 0, 0]
def cut(str, len = WIDTH):
	return str
def fil(a, le):
	b = a
	while len(b) < le:
		b += ' '
	b += '|'
	#print(b)
	return b
def leng(a):
	t = 0
	for i in range(len(a)):
		t += 1
		if re.match(r'[\u4e00-\u9fa5]', a[i]):
			t += 1
	return t
for i in range(len(mn)):
	line = mn[i].strip()
	if cen:
		center.append(i)
	if boks:
		box.append(i)
	if not line.startswith('.si'):
		cen = False
	if line.startswith('.mt'):
		cen = True
		out += '\n\n\n\n\n\n\n\n\n\n'
		continue
	if line.startswith('.au'):
		cen = False
		out += '\n\n\n'
		continue
	if line.startswith('.si'):
		cen = True
		out += '\t'
		continue
	if (line.startswith('box center') or line.startswith('center box')) and line.endswith(';'):
		cen = True
		boks = True
		out += '-boxs-\n'
		continue
	if line.startswith(".TE"):
		cen = False
		boks = False
		out += '-boxe-\n'
		continue
	if line.startswith('.hn '):
		num = eval(line[4:])
		hn[num] += 1
		for j in range(num + 1, len(hn)):
			hn[j] = 0
		for j in range(1, num + 1):
			out += str(hn[j]) + '.'
		out += ' '
		continue
	if line.startswith('.ds') or line.startswith('.so') or line.startswith('.\\\"') \
	   or line.startswith(".BR") or line.startswith(".ft") or line.startswith(".TS") \
	   or line.startswith(".sd") or line.startswith(".ed") or line.startswith(".ei") \
	   or line.startswith(".ce") or line.startswith(".if") or line.startswith(".L") \
	   or line.startswith(".tr") or line.startswith('C C.') or line.startswith('\\*(f2') or line == '.':
		continue
	if line == '.pg':
		continue
		out += '    '
		continue
	if line == 'L.':
		continue
	if line.startswith('.op '):
		out = out.rstrip('\n') + line[4:]
		continue
	if line.startswith('.lp '):
		out += line[4:].strip('"') + '\t'
		continue
	if boks:
		out += '|'
	out += line
	if boks:
		out += ''
	out += '\n'
out = out.replace('\\fB', '').replace('\\fP', '').replace('\\(oq', '‘') \
		.replace('\\(cq', '’').replace('\\fR', '').replace('\\fI', '') \
		.replace('\\(lq', '“').replace('\\(rq', '”').replace('\\f(CR', '') \
		.replace('(tab))', '').replace('(tab)', '         ').replace('\\(ha', '^') \
		.replace('\\\\', '\\').replace('\\-', '-').replace('\\&_', '_') \
		.replace('\\&=', '=').replace('\\\'', '\'').replace('\\.', '.') \
		.replace('\\`', '').replace('\\(dq', '').replace('\\(ti', '') \
		.replace('.sp 1', '').replace('\\*(f2', '')
outlines = out.split('\n')
longest = 0
boxs = 0
boxe = 0
boks = False
sande = ([0], [0], [0])
for i in range(len(outlines)):
	line = outlines[i]
	if line.startswith('-boxe-'):
		boks = False
		boxe = i
		#print('boxs, boxe啊', boxs, boxe)
		if not boxs == sande[0][-1]:
			sande[0].append(boxs)
			sande[1].append(boxe)
			sande[2].append(longest)
			longest = 0
	if boks:
		longest = max(longest, len(line))
		if i > 100:
			outlines[i] = outlines[i].replace('@', '\\')
	if line.startswith('-boxs-'):
		boxs = i
		boks = True
#print(sande)
for i in range(1, len(sande[0])):
	for j in range(sande[0][i], sande[1][i]):
		#print('filling:', fil(outlines[j], sande[2][i]))
		outlines[j] = fil(outlines[j], sande[2][i])
	#outlines[sande[0][i]] = sande[2][i] * '-' + '|'
	#outlines[sande[1][i]] = sande[2][i] * '-' + '|'
def phind(a, b):
	for i in range(len(a)):
		if a[i] == b:
			return i
	return 0
def senter(a, b):
	#b长a短
	#print('a, b, lena, lenb', a, b, leng(a), leng(b))
	c = a
	d = leng(b)
	e = leng(a)
	s = 0
	long = int((leng(b) - leng(a)) / 2)
	#print(long)
	for k in range(len(b)):
		if leng(b[:k]) == long:
			return b[:long] + a + b[long + leng(a):]
		if leng(b[:k]) - long == 1:
			s = leng(b[k])
	return b[:s] + a + b[s + leng(a):]
nc = 0
fucklines = {
	r'|y k u         7 8 9                  |' : r'|       y k u          7 8 9      |',
	r'|\ | /         \ | /                  |' : r'|       \ | /          \ | /      |',
	r'|h-.-l         4-.-6                  |' : r'|       h-.-l          4-.-6      |',
	r'|/ | \         / | \                  |' : r'|       / | \          / | \      |',
	r'|b j n         1 2 3                  |' : r'|       b j n          1 2 3      |',
	r'|（关闭number_pad）         （开启number_pad）|' : r'|  关闭number_pad  开启number_pad  |'
}
with open('./Guidebook.txt', 'w') as f:
	for i in range(len(outlines)):
		if nc:
			nc = False
			continue
		if outlines[i].startswith('-boxe-'):
			if not i in sande[1]:
				continue
			d = '+'
			for j in range(sande[2][phind(sande[1], i)] - 1):
				d += '-'
			d += '+'
			print(senter(outlines[i + 1], d), file = f)
			nc = True
			continue
		if outlines[i].startswith('-boxs-'):
			d = '+'
			for j in range(sande[2][phind(sande[0], i)] - 1):
				d += '-'
			d += '+'
			print(d, file = f)
			continue
		if outlines[i].lstrip().startswith('.sm'):
			continue
		if outlines[i] in fucklines.keys():
			print(fucklines[outlines[i]], file = f)
			continue
		print(outlines[i], file = f)
