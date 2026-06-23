#!/usr/bin/env python3
"""
guidebook_mn2html.py

Best-effort converter for NetHack's Guidebook.mn (roff/troff-style source)
to a standalone HTML document.

This is not a byte-identical clone of the original NetHack site generator.
It is a practical reverse-engineered converter that preserves the document
structure, headings, paragraphs, definition rows, tables/code blocks, and
common roff escapes used by Guidebook.mn.
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from typing import List, Tuple
import sys

SPECIALS = {
    r'\(lq': '“', r'\(rq': '”', r'\(oq': '‘', r'\(cq': '’',
    r'\(dq': '"', r'\(rs': '\\', r'\(em': '—', r'\(en': '–',
    r'\(hy': '-', r'\(mi': '-', r'\(ha': '^', r'\(ti': '~',
    r'\(bv': '|', r'\(ul': '_', r'\(aa': '´', r'\(ga': '`',
}

FONT_OPEN = {
    'B': 'strong',
    'I': 'em',
    'R': 'code',
    'P': None,
    'CB': 'strong',
    'CI': 'em',
    'CR': 'code',
}

STYLE = r'''@font-face {
  font-family: "Atkinson Hyperlegible Mono";
  font-weight: bold;
  unicode-range: U+000-5FF; 
  font-display: swap;
  src:
    local("Atkinson Hyperlegible Mono"),
    url(https://www.nethack.org/download/font/AtkinsonHyperlegibleMono-Bold.woff2) format("woff2"),
    url(https://www.nethack.org/download/font/AtkinsonHyperlegibleMono-Bold.ttf) format("truetype")
}

@font-face {
  font-family: "Atkinson Hyperlegible Mono";
  font-weight: normal;
  unicode-range: U+000-5FF; 
  font-display: swap;
  src:
    local("Atkinson Hyperlegible Mono"),
    url(https://www.nethack.org/download/font/AtkinsonHyperlegibleMono-Regular.woff2) format("woff2"),
    url(https://www.nethack.org/download/font/AtkinsonHyperlegibleMono-Regular.ttf) format("truetype")
}
@font-face {
  font-family: "Atkinson Hyperlegible Next";
  font-weight: bold;
  unicode-range: U+000-5FF; 
  font-display: swap;
  src:
    local("Atkinson Hyperlegible Next"),
    url(https://www.nethack.org/download/font/AtkinsonHyperlegibleNext-Bold.woff2) format("woff2"),
    url(https://www.nethack.org/download/font/AtkinsonHyperlegibleNext-Bold.ttf) format("truetype")
}
@font-face {
  font-family: "Atkinson Hyperlegible Next";
  font-weight: normal;
  unicode-range: U+000-5FF; 
  font-display: swap;
  src:
    local("Atkinson Hyperlegible Next"),
    url(https://www.nethack.org/download/font/AtkinsonHyperlegibleNext-Regular.woff2) format("woff2"),
    url(https://www.nethack.org/download/font/AtkinsonHyperlegibleNext-Regular.ttf) format("truetype")
}
@font-face {
  font-family: "Atkinson Hyperlegible Mono";
  font-weight: bold;
  font-style: italic;
  unicode-range: U+000-5FF; 
  font-display: swap;
  src:
    local("Atkinson Hyperlegible Mono"),
    url(https://www.nethack.org/download/font/AtkinsonHyperlegibleMono-BoldItalic.woff2) format("woff2"),
    url(https://www.nethack.org/download/font/AtkinsonHyperlegibleMono-BoldItalic.ttf) format("truetype")
}
@font-face {
  font-family: "Atkinson Hyperlegible Mono";
  font-weight: normal;
  font-style: italic;
  unicode-range: U+000-5FF; 
  font-display: swap;
  src:
    local("Atkinson Hyperlegible Mono"),
    url(https://www.nethack.org/download/font/AtkinsonHyperlegibleMono-RegularItalic.woff2) format("woff2"),
    url(https://www.nethack.org/download/font/AtkinsonHyperlegibleMono-RegularItalic.ttf) format("truetype")
}
@font-face {
  font-family: "Atkinson Hyperlegible Next";
  font-weight: bold;
  font-style: italic;
  unicode-range: U+000-5FF; 
  font-display: swap;
  src:
    local("Atkinson Hyperlegible Next"),
    url(https://www.nethack.org/download/font/AtkinsonHyperlegibleNext-BoldItalic.woff2) format("woff2"),
    url(https://www.nethack.org/download/font/AtkinsonHyperlegibleNext-BoldItalic.ttf) format("truetype")
}
@font-face {
  font-family: "Atkinson Hyperlegible Next";
  font-weight: normal;
  font-style: italic;
  unicode-range: U+000-5FF; 
  font-display: swap;
  src:
    local("Atkinson Hyperlegible Next"),
    url(https://www.nethack.org/download/font/AtkinsonHyperlegibleNext-RegularItalic.woff2) format("woff2"),
    url(https://www.nethack.org/download/font/AtkinsonHyperlegibleNext-RegularItalic.ttf) format("truetype")
}


.nhbody {
    font-size:100%
}

.nhfont-r-system {
  font-family: serif;
  font-style: normal;
}
.nhfont-r-atkinsonhyper {
  font-family: "Atkinson Hyperlegible Next";
  font-style: normal;
}

.nhfont-mb-system {
  font-family: serif;
  font-weight: bold;
}
.nhfont-mb-atkinsonhyper {
  font-family: "Atkinson Hyperlegible Mono";
  font-weight: bold;
}

.nhfont-m-system {
  font-family: monospace;
}
.nhfont-m-atkinsonhyper {
  font-family: "Atkinson Hyperlegible Mono";
  font-weight: normal;
}

.nhfont-b-system {
  font-weight: bold;
}
.nhfont-b-atkinsonhyper {
  font-family: "Atkinson Hyperlegible Next";
  font-weight: bold;
}

.nhfont-bim-system {
  font-weight: bold;
  font-style: italic;
}
.nhfont-bim-atkinsonhyper {
  font-family: "Atkinson Hyperlegible Mono";
  font-weight: bold;
  font-style: italic;
}

.nhfont-im-system {
  font-style: italic;
}
.nhfont-im-system {
  font-family: "Atkinson Hyperlegible Mono";
  font-style: italic;
}

.nhfont-bi-system {
  font-weight: bold;
  font-style: italic;
}
.nhfont-bi-atkinsonhyper {
  font-family: "Atkinson Hyperlegible Next";
  font-weight: bold;
  font-style: italic;
}




.nhfont-i-system {
  font-style: italic;
}
.nhfont-i-atkinsonhyper {
  font-family: "Atkinson Hyperlegible Next";
  font-style: italic;
}




header.nhtheme-color.nhlayout-normal {
    padding: .75em 0 0 0;
    background-color:#00cc00;
    border-radius:10px;
}
header.nhtheme-bw.nhlayout-normal {
    padding: .75em 0 0 0;
    background-color:#dcdcdc;
    border-radius:10px;
}
header.nhtheme-color.nhlayout-simple {
    padding: .75em 0 0 0;
}
header.nhtheme-bw.nhlayout-simple {
    padding: .75em 0 0 0;
}




.navrow {
    box-sizing: border-box;
    height: 2em;
}
.navrow::after {
  content: "";
  display: table;
  clear: both;
}
.navrowlft {
    float: left;
    width: 30%;
    position: relative;
}
#accesslinkwrapper {
    position: absolute;
    top: 0%;
}
#englinkwrapper {
    float: right;
    width: 30%;
    text-align: right;
    position: relative;
    top: 0%;
}
.navrowctr {
    float: left;
    width: 40%;
    text-align: center;
}
.navrowrit {
    float: right;
    width: 30%;
    text-align: right;
}
.accshape {
    background-color: white;
    border-radius:7px;
}

.acclink {
    position: absolute;
    left:-10000px;
    top:auto;
    width:1px;
    height:1px;
    overflow:hidden;
}
.acclink:focus {
    height:auto;
    position:static;
    width:auto;
}
acclinkwrap {
    margin:0;
    width:33%;
}


footer.nhtheme-color.nhlayout-normal {
    padding: .75em 0 0 0;
    background-color:#00cc00;
    border-radius:10px;
}
footer.nhtheme-bw.nhlayout-normal {
    padding: .75em 0 0 0;
    background-color:#dcdcdc;
    border-radius:10px;
}
footer.nhtheme-color.nhlayout-simple {
    padding: .75em 0 0 0;
}
footer.nhtheme-bw.nhlayout-simple {
    padding: .75em 0 0 0;
}






hr.nhtheme-color.nhlayout-normal.nhhide {
    display:none;
}
hr.nhtheme-bw.nhlayout-normal.nhhide {
    display:none;
}
hr.nhtheme-color.nhlayout-simple.nhhide {
    height:3px;
    border-width:0;
    color:purple;
    background-color:#9932cc;       
}
hr.nhtheme-bw.nhlayout-simple.nhhide {
    height:3px;
    border-width:0;
    color:black;
    background-color:black;
}


hr.nhtheme-color {
    height:3px;
    border-width:0;
    color:purple;
    background-color:#9932cc;       
}
hr.nhtheme-bw {
    height:3px;
    border-width:0;
    color:black;
    background-color:black;
}

h1.nhtheme-color {
    color:green;
}
h1.nhtheme-bw {
    color:black;
}
h2.nhtheme-color {
    color:green;
}
h2.nhtheme-bw {
    color:black;
}




.nhborder.nhtheme-color.nhlayout-simple {


}
.nhborder.nhtheme-color.nhlayout-normal {
    border-style: solid;
    border-width: 3px;
    border-color: #00cc00;
    border-radius: 10px;
}
.nhborder.nhtheme-bw.nhlayout-simple {


}
.nhborder.nhtheme-bw.nhlayout-normal {
    border-style: solid;
    border-width: 3px;
    border-color: black;
    border-radius: 10px;
}


.newsentry-date {
 font-size:80%;
 vertical-align: middle;
}


.indent5p {
    padding-left: 5%;
}
'''

def center_to_table(input_text):
    lines = input_text.split('\n')
    out_html = []
    tr_map = {}
    
    in_table = False
    table_options = []
    table_alignments = []
    table_rows = []
    tab_char = '\t'
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 1. 解析 roff 的 .tr 翻译指令
        if line.startswith('.tr '):
            mapping_str = line[4:]
            tokens = []
            idx = 0
            while idx < len(mapping_str):
                # 解析 roff 的特殊转义符
                if mapping_str.startswith(r'\(rs', idx):
                    tokens.append('\\')
                    idx += 4
                elif mapping_str.startswith(r'\-', idx):
                    tokens.append('−')  # U+2212 减号
                    idx += 2
                else:
                    tokens.append(mapping_str[idx])
                    idx += 1
            
            # 成对建立翻译映射
            for j in range(0, len(tokens) - 1, 2):
                tr_map[tokens[j]] = tokens[j+1]
                
        # 2. 捕获 tbl 开始指令
        elif line.startswith('.TS'):
            in_table = True
            table_options = []
            table_alignments = []
            table_rows = []
            tab_char = '\t'
            
            # 提取表格选项
            i += 1
            if i < len(lines):
                opt_line = lines[i].strip()
                if opt_line.endswith(';'):
                    opts = opt_line[:-1].split()
                    for opt in opts:
                        if opt.startswith('tab('):
                            tab_char = opt[4]
                        else:
                            table_options.append(opt)
                    i += 1
                    fmt_line = lines[i].strip()
                else:
                    fmt_line = opt_line
                
                # 提取格式对齐指令 (以 . 结尾)
                while i < len(lines) and not fmt_line.endswith('.'):
                    i += 1
                    fmt_line += ' ' + lines[i].strip()
                
                fmt_str = fmt_line.strip().strip('.')
                table_alignments = fmt_str.split()
                
        # 3. 捕获 tbl 结束指令，并生成 HTML
        elif line.startswith('.TE'):
            in_table = False
            
            # 组合表格 Style
            table_styles = ["font:normal 14px monospace"]
            if "center" in table_options:
                table_styles.append("margin:auto")
            if "box" in table_options:
                table_styles.append("border:1px solid black")
            
            # 对数据应用翻译表并按分隔符拆分列
            processed_rows = []
            for row in table_rows:
                translated = "".join(tr_map.get(c, c) for c in row)
                cells = translated.split(tab_char)
                processed_rows.append(cells)
                
            num_cols = len(table_alignments)
            widths = []
            
            # 还原宽度计算逻辑
            for c in range(num_cols):
                max_len = 0
                for row in processed_rows:
                    if c < len(row):
                        cell = row[c]
                        # 原脚本会将 \f 认定为单一字符计算长度（模拟计算法：将\f替换为单字符_）
                        simulated = cell.replace('\\f', '_')
                        if len(simulated) > max_len:
                            max_len = len(simulated)
                # 1.4倍字符长度的固定转换
                widths.append(max_len * 1.4)
                
            html = f'<div><table style="{";".join(table_styles)}"><tbody>'
            
            for row in processed_rows:
                html += '<tr>'
                for c in range(num_cols):
                    align = 'center'
                    if c < len(table_alignments):
                        if table_alignments[c] == 'L': align = 'left'
                        elif table_alignments[c] == 'C': align = 'center'
                        elif table_alignments[c] == 'R': align = 'right'
                    
                    width = widths[c] if c < len(widths) else 0.0
                    cell_text = row[c] if c < len(row) else ""
                    
                    html += f'<td style="text-align:{align};width:{width:.1f}ch">'
                    
                    if not cell_text:
                        html += '&nbsp;'
                    else:
                        # 剥离格式符号 \fX
                        cleaned = re.sub(r'\\f[a-zA-Z]', '', cell_text)
                        if not cleaned:
                            html += '&nbsp;'
                        else:
                            # 预转义 HTML 特殊实体
                            #cleaned = cleaned.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                            cleaned = cleaned.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                            
                            # 核心漏洞/逻辑：仅包裹可打印 ASCII 区间的字符 (这是为什么输出1中的 U+2212 特殊减号会被留在 span 外部的原因)
                            cleaned = re.sub(r'([\x21-\x7E]+)', r'<span style="font:normal 14px monospace">\1</span>', cleaned)
                            
                            # 空格转换
                            #cleaned = cleaned.replace(' ', '&nbsp;')
                            cleaned = cleaned.replace('&nbsp;', ' ')
                            html += cleaned
                            
                    html += '</td>'
                html += '</tr>'
            html += '</tbody></table></div>'
            out_html.append(html)
            #print(html)
        elif in_table:
            table_rows.append(line)
        else:
            out_html.append(line)
            
        i += 1
        
    return '\n'.join(out_html)
class GuidebookRoffToHTML:
    def __init__(self, src: str):
        self.lines = src.splitlines()
        self.strings: dict[str, str] = {}
        self.out: List[str] = []
        self.toc: List[Tuple[int, str, str, str]] = []
        self.counts = [0] * 8
        self.par: List[str] = []
        self.title_lines: List[str] = []
        self.author_lines: List[str] = []
        self.center_pending: int = 0

    def define_string(self, name: str, value: str) -> None:
        self.strings[name] = value

    def expand_strings(self, s: str) -> str:
        def repl(m: re.Match[str]) -> str:
            key = m.group(1) if m.group(1) is not None else m.group(2)
            return self.strings.get(key, "")

        s = re.sub(r'\\\*\(([^)\s]{1,16})\)', repl, s)
        s = re.sub(r'\\\*\[([^\]]+)\]', repl, s)
        return s

    def inline_html(self, s: str) -> str:
        s = self.expand_strings(s)
        out: List[str] = []
        stack: List[str] = []
        i = 0
        while i < len(s):
            ch = s[i]
            if ch == '\\' and i + 1 < len(s):
                nxt = s[i + 1]

                if nxt == '(' and i + 3 < len(s):
                    code = s[i + 2:i + 4]
                    key = r'\(%s' % code
                    if key in SPECIALS:
                        out.append(SPECIALS[key])
                        i += 4
                        continue

                if nxt == 'f':
                    if s.startswith(r'\fP', i):
                        if stack:
                            out.append(f'</{stack.pop()}>')
                        i += 3
                        continue

                    if i + 2 < len(s) and s[i + 2] == '(' and i + 5 <= len(s):
                        code = s[i + 3:i + 5]
                        tag = FONT_OPEN.get(code)
                        if tag:
                            out.append(f'<{tag}>')
                            stack.append(tag)
                        i += 5
                        continue

                    if i + 2 < len(s):
                        code = s[i + 2]
                        tag = FONT_OPEN.get(code)
                        if tag:
                            out.append(f'<{tag}>')
                            stack.append(tag)
                        i += 3
                        continue

                if nxt == '-':
                    out.append('-')
                    i += 2
                    continue
                if nxt == '&':
                    i += 2
                    continue
                if nxt == ' ':
                    out.append(' ')
                    i += 2
                    continue
                if nxt == ':':
                    i += 2
                    continue
                if nxt == 'c':
                    i += 2
                    continue
                if nxt in ("`", "'"):
                    out.append(nxt)
                    i += 2
                    continue

            out.append(html.escape(ch, quote=False))
            i += 1

        while stack:
            out.append(f'</{stack.pop()}>')
        return ''.join(out)

    def sec_id(self, level: int) -> str:
        parts = [str(self.counts[i]) for i in range(level) if self.counts[i] > 0]
        return "toc_" + ".".join(parts)

    def emit_para(self) -> None:
        if not self.par:
            return
        text = " ".join(p.strip() for p in self.par if p.strip())
        self.par = []
        if text:
            self.out.append(f'<p>{self.inline_html(text)}</p>')


    def emit_title_block(self) -> None:
        if not self.title_lines:
            return
        self.out.append('<div class="titleblock">')
        for idx, line in enumerate(self.title_lines):
            cls = 'title' if idx < 2 else 'subtitle'
            self.out.append(f'<div class="{cls}">{self.inline_html(line)}</div>')
        self.out.append('</div>')
        self.title_lines = []

    def emit_author_block(self) -> None:
        if not self.author_lines:
            return
        self.out.append('<div class="authorblock">')
        for line in self.author_lines:
            self.out.append(f'<div class="author">{self.inline_html(line)}</div>')
        self.out.append('</div>')
        self.author_lines = []

    def emit_center_line(self, line: str) -> None:
        text = line.strip()
        if not text:
            return
        # .ce N in roff centers the next N output lines.
        # Emit a visible block-level centered paragraph so the result is obvious.
        self.out.append('<!-- centered by .ce -->')
        self.out.append(f'<p class="center centered-line">{self.inline_html(text)}</p>')

    def emit_heading(self, level: int, title: str) -> None:
        self.emit_para()
        idx = level - 1
        if idx >= len(self.counts):
            self.counts += [0] * (idx - len(self.counts) + 1)
        self.counts[idx] += 1
        for j in range(idx + 1, len(self.counts)):
            self.counts[j] = 0

        sec = ".".join(str(self.counts[i]) for i in range(level) if self.counts[i] > 0)
        hid = self.sec_id(level)
        self.toc.append((level, sec, title, hid))
        tag = f'h{min(level + 1, 5)}'
        self.out.append(f'<{tag} id="{hid}">{sec}. {self.inline_html(title)}</{tag}>')

    def emit_pre(self, lines: List[str], centered: bool = False) -> None:
        if not lines:
            return
        esc_lines = [self.inline_html(line) for line in lines]
        block = "\n".join(esc_lines)
        #if centered:
            #self.out.append(r'''<tbody><tr><td style="text-align:center;width:26.6ch">''' + block + '''</td></tr></tbody>''')
            #self.out.append('<div class="table-center"><pre class="center-pre">' + block + '</pre></div>')
        #else:
        self.out.append('<div style="text-indent:0ch;margin-left:10ch">' + block + '</div>')

    def emit_list(self, rows: List[Tuple[str, str]]) -> None:
        if not rows:
            return
        self.out.append('<div class="listblock"><dl>')
        for label, desc in rows:
            self.out.append(f'<div><span data-nh="1" style="display:inline-block;vertical-align:top;text-indent:0ch;width:5.1ch"><span style="font:normal 16px serif">{self.inline_html(label)}</span></span><span data-nh="2" style="display:inline-block;width:2ch;vertical-align:top">&nbsp;<span style="font:normal 16px serif">-</span></span><span data-nh="3" style="display:inline-block;width:calc(95% - 5.1ch)"><span style="font:normal 16px serif">{self.inline_html(desc)}</span>&nbsp;<span style="font:normal 16px serif"> </span></span></div>')
        self.out.append('</dl></div>')

    def parse(self) -> None:
        i = 0
        list_rows: List[Tuple[str, str]] = []
        list_mode = False

        while i < len(self.lines):
            raw = self.lines[i]
            line = raw.lstrip()
            # 直接输出由 center_to_table 生成的表格 HTML（整行，已包含外层的 <div>）
            if line.startswith('<div><table'):
                self.emit_para()          # 先输出之前缓存的段落
                self.out.append(raw.strip())   # 表格行原样输出，不做任何转义
                i += 1
                continue

            if line == '.':
                self.emit_para()
                i += 1
                continue

            if line.startswith('.\\"'):
                i += 1
                continue

            if line.startswith('.de '):
                i += 1
                while i < len(self.lines) and self.lines[i].strip() != '..':
                    i += 1
                i += 1
                continue

            if line.startswith('.if ') or line.startswith('.ie ') or line.startswith('.el ') or \
               line.startswith('.po') or line.startswith('.ll') or line.startswith('.lt') or \
               line.startswith('.tm') or line.startswith('.rm') or line.startswith('.ab') or \
               line.startswith('.so') or line.startswith('.sm') or line.startswith('.nr') or \
               line.startswith('.tr') or line.startswith('.in'):
                i += 1
                continue

            if line.startswith('.ds '):
                parts = line.split(None, 2)
                if len(parts) >= 3:
                    self.define_string(parts[1], parts[2])
                i += 1
                continue

            if line.startswith('.mt'):
                self.emit_para()
                i += 1
                while i < len(self.lines) and not self.lines[i].lstrip().startswith('.'):
                    if self.lines[i].strip():
                        self.title_lines.append(self.lines[i].strip())
                    i += 1
                self.emit_title_block()
                continue

            if line.startswith('.au'):
                self.emit_para()
                i += 1
                while i < len(self.lines) and not self.lines[i].lstrip().startswith('.'):
                    if self.lines[i].strip():
                        self.author_lines.append(self.lines[i].strip())
                    i += 1
                self.emit_author_block()
                continue

            if line.startswith('.hn'):
                self.emit_para()
                parts = line.split(None, 1)
                if len(parts) > 1 and parts[1].strip().isdigit():
                    level = int(parts[1].strip())
                    i += 1
                    self.out.append('<div><table width="100%%"><tbody><tr><td width="33%" style="text-align:left">NetHack 5.0.0</td><td width="33%" style="text-align:center">2026.06.21</td><td width="33%" style="text-align:right">[<a href="#_TOC">目录</a>]</td></tr></tbody></table></div><hr><br>')
                    while i < len(self.lines) and not self.lines[i].strip():
                        i += 1
                    if i < len(self.lines) and not self.lines[i].lstrip().startswith('.'):
                        title = self.lines[i].strip()
                        self.emit_heading(level, title)
                        i += 1
                        continue
                if len(parts) == 1:
                    i += 1
                    while i < len(self.lines) and not self.lines[i].strip():
                        i += 1
                    if i < len(self.lines) and not self.lines[i].lstrip().startswith('.'):
                        title = self.lines[i].strip()
                        level = self.toc[-1][0] if self.toc else 1
                        self.emit_heading(level, title)
                        i += 1
                        continue
                i += 1
                continue

            if line.startswith('.op '):
                opt = line[4:].strip()
                if opt.startswith('"') and opt.endswith('"') and len(opt) >= 2:
                    opt = opt[1:-1]
                self.par.append(opt)
                i += 1
                continue

            if line.startswith('.UR '):
                url = line[4:].strip()
                self.par.append(url)
                i += 1
                continue

            if line.startswith('.UX'):
                self.par.append('UNIX')
                i += 1
                continue

            if line.startswith('.pg'):
                self.emit_para()
                i += 1
                continue

            if line.startswith('.lp'):
                self.emit_para()
                label = line[3:].strip()
                if label.startswith('"') and label.endswith('"') and len(label) >= 2:
                    label = label[1:-1]
                if label:
                    i += 1
                    body: List[str] = []
                    while i < len(self.lines) and not self.lines[i].lstrip().startswith('.'):
                        if self.lines[i].strip():
                            body.append(self.lines[i].strip())
                        else:
                            break
                        i += 1
                    self.out.append(
                        f'<div class="lp"><span class="label">{self.inline_html(label)}</span> '
                        f'{self.inline_html(" ".join(body))}</div>'
                    )
                    continue
                i += 1
                continue

            if line.startswith('.ce'):
                # roff/troff syntax: .ce N centers the next N output lines
                self.emit_para()
                parts = line.split()
                n = 1
                if len(parts) > 1:
                    try:
                        n = int(parts[1])
                    except ValueError:
                        n = 1
                self.center_pending = max(0, n)
                i += 1
                continue

            if line.startswith('.sp'):
                self.emit_para()
                i += 1
                continue

            if line.startswith('.BR'):
                self.emit_para()
                self.out.append('<br>')
                i += 1
                continue

            if line.startswith('.TE'):
                i += 1
                continue
            if line.startswith('.TS'):
                i += 1
                continue
                self.emit_para()
                pre_lines: List[str] = []
                centered = False
                i += 1
                while i < len(self.lines):
                    l2 = self.lines[i].rstrip('\n')
                    s2 = l2.lstrip()

                    if s2.startswith('.TE'):
                        break

                    if not pre_lines and s2.strip().lower() == 'center;':
                        centered = True
                        i += 1
                        continue

                    if s2.startswith(('.ft ', '.ft', '.BR', '.ce', '.if ', '.\\"', '.tr', '.nr', '.po', '.ll', '.lt')):
                        i += 1
                        continue

                    pre_lines.append(self.lines[i] if not l2.startswith('.') else l2)
                    i += 1
                self.emit_pre(pre_lines)
                while i < len(self.lines) and not self.lines[i].lstrip().startswith('.TE'):
                    i += 1
                if i < len(self.lines):
                    i += 1
                continue
 
            if line.startswith('.PS'):
                self.emit_para()
                list_rows = []
                list_mode = True
                i += 1
                continue

            if line.startswith('.PE'):
                if list_rows:
                    self.emit_list(list_rows)
                list_rows = []
                list_mode = False
                i += 1
                continue

            if line.startswith('.SD') or line.startswith('.sd') or line.startswith('.si'):
                self.emit_para()
                pre_lines: List[str] = []
                depth = 1
                i += 1
                while i < len(self.lines) and depth > 0:
                    l2 = self.lines[i].lstrip()
                    if l2.startswith(('.SD', '.sd', '.si')):
                        depth += 1
                        i += 1
                        continue
                    if l2.startswith(('.ED', '.ed', '.ei')):
                        depth -= 1
                        i += 1
                        continue
                    if l2.startswith(('.ft ', '.ft', '.if ', '.\\"', '.po', '.ll', '.lt', '.tr', '.nr')):
                        i += 1
                        continue
                    pre_lines.append(self.lines[i] if not l2.startswith('.') else l2)
                    i += 1
                self.emit_pre(pre_lines)
                continue

            if line.startswith('.ED') or line.startswith('.ed') or line.startswith('.ei'):
                i += 1
                continue

            if line.startswith('.PL '):
                label = line[4:].strip()
                if label.startswith('"') and label.endswith('"') and len(label) >= 2:
                    label = label[1:-1]
                i += 1
                desc: List[str] = []
                while i < len(self.lines) and not self.lines[i].lstrip().startswith('.'):
                    if self.lines[i].strip():
                        desc.append(self.lines[i].strip())
                    else:
                        break
                    i += 1
                if list_mode:
                    list_rows.append((label, " ".join(desc)))
                else:
                    self.out.append(
                        f'<div class="lp"><span class="label">{self.inline_html(label)}</span> '
                        f'{self.inline_html(" ".join(desc))}</div>'
                    )
                continue

            if line.startswith('.CC '):
                rest = line[4:].strip()
                m = re.match(r'^(\S+)\s+(.*)$', rest)
                if m:
                    label, desc = m.group(1), m.group(2).strip()
                    if desc.startswith('"') and desc.endswith('"') and len(desc) >= 2:
                        desc = desc[1:-1]
                    if list_mode:
                        list_rows.append((label, desc))
                    else:
                        self.out.append(
                            f'<div class="lp"><span class="label">{self.inline_html(label)}</span> '
                            f'{self.inline_html(desc)}</div>'
                        )
                i += 1
                continue

            if line.startswith(('.ft ', '.ft', '.hw', '.nr', '.sm', '.tr', '.in', '.po', '.ll', '.lt', '.if', '.ie', '.el', '.rm', '.ab', '.so')):
                i += 1
                continue

            if not line.strip():
                self.emit_para()
                i += 1
                continue

            if self.center_pending > 0 and line and not line.startswith('.'):
                self.emit_para()
                self.emit_center_line(raw)
                self.center_pending -= 1
                i += 1
                continue

            if list_mode and list_rows and not list_rows[-1][1]:
                label, _ = list_rows.pop()
                list_rows.append((label, raw.strip()))
            else:
                self.par.append(raw)
            i += 1

        self.emit_para()
        if list_rows:
            self.emit_list(list_rows)

    def build_toc(self) -> str:
        if not self.toc:
            return ''
        parts = []
        cur = 0
        for lvl, sec, title, hid in self.toc:
            while cur < lvl:
                parts.append('<ul>')
                cur += 1
            while cur > lvl:
                parts.append('</ul>')
                cur -= 1
            parts.append(f'<li><a href="#{hid}">{html.escape(sec)}. {self.inline_html(title)}</a></li>')
        while cur > 0:
            parts.append('</ul>')
            cur -= 1
        parts.append('</nav>')
        return "\n".join(parts)

    def convert(self) -> str:
        self.parse()
        body = "\n".join(self.out)
        toc = self.build_toc()
        return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NetHack说明手册</title>
<style>
/*body{{font-family:serif; max-width: 980px; margin: 0 auto; padding: 24px; line-height:1.4; color:#111; background:#fff}}*/
/*h1,h2,h3,h4,h5{{margin:1.2em 0 0.5em}}*/
p{{text-indent:5ch;margin-left:5ch}}
.center{{text-align:center}}
.centered-line{{text-align:center; margin:0.9em 0; font-weight:bold}}
.titleblock{{margin:1.5em 0 2em}}
.titleblock .title{{text-align:center; font-size:1.8em; font-weight:bold}}
.titleblock .subtitle{{text-align:center; font-size:1.15em; font-style:italic}}
.authorblock{{margin:0.5em 0 1.2em}}
.author{{text-align:center; font-style:italic}}
.lp{{margin:0.45em 0 0.45em 1.5em; text-indent:-1.5em}}
.lp .label{{font:normal 15px serif; text-indent: 5ch; display:inline-block; min-width:10ch; font-weight:bold}}
/*
.toc{{border:1px solid #ddd; border-radius:12px; padding:16px 18px; margin:0 0 2em 0; background:#fafafa}}
.toc ul{{margin:0.35em 0 0.35em 1.3em}}
*/
pre{{white-space:pre-wrap; background:#fafafa; border:1px solid #e0e0e0; border-radius:10px; padding:12px; overflow-x:auto}}
.listblock dl{{margin:0.5em 0 0.5em 1.4em;text-indent: 0ch;margin-left: 15ch;}}
.listblock dt{{font-weight:bold; margin-top:0.4em}}
.listblock dd{{margin:0 0 0.4em 1.2em}}
.table-center{{text-align:center;}}
.center-pre{{display:inline-block; text-align:left; margin:0 auto;}}
code{{font-family:monospace}}
strong{{font-weight:bold}}
em{{font-style:italic}}
{STYLE}
</style>
</head>
<body class="nhbody">
<header class="nhtheme nhlayout nhfont nhfont-r nhtheme-color nhfont-r-system nhfont-system nhlayout-normal">
 <div class="navrow">
 <div class="navrowlft">
&nbsp; 
 <div id="accesslinkwrapper"><span id="acclinkwrap"><a class="accshape acclink" href="#mainskip">Skip to main</a></span> <a class="accshape" href="https://www.nethack.org/common/accessibility.html">无障碍</a></div>
 </div>
 <div class="navrowctr">
[&nbsp;
<a href="../index.html">返回主页</a>
&nbsp;|&nbsp;
<a href="https://www.nethack.org/common/index.html">5.0.0版</a>
&nbsp;|&nbsp;
<a href="../contact/index.html">联系我们</a>
&nbsp;]
 </div>
<div class="navrowrit">
&nbsp;<div id="englinkwrapper"><span id="englinkwrap"><a class="accshape acclink" href="#mainskip">Skip to main</a></span> <a class="accshape" href="https://www.nethack.org/v500/Guidebook.html">English</a></div>
</div>
</header>
<div role="main" id="mainskip">
没有
<a href="http://www.nethack.org/download/5.0.0/nethack-500-Guidebook.pdf">pdf</a>
，因为我懒。（<a href="https://www.gnu.org/software/groff/">用来parse这个文本的工具</a>年龄比我都大！）但有
<a href="http://www.nethack.org/download/5.0.0/nethack-500-Guidebook.txt">ASCII</a>
。
<hr>
<h2 style="text-align:center">
 <a id="_TOC">目录</a>
</h2>
<br>
<div style="font-size:16px">
<div style="display:flex;justify-content:center">
{toc}
</div>
{body}
</div>
</div>
</body>
</html>
"""


def main() -> None:
    ap = argparse.ArgumentParser(description="Convert NetHack Guidebook.mn to HTML.")
    ap.add_argument("input", type=Path, help="Path to Guidebook.mn")
    ap.add_argument("-o", "--output", type=Path, default=Path("Guidebook.html"), help="Output HTML path")
    args = ap.parse_args()

    src = args.input.read_text("utf-8", errors="replace").replace('(tab)', '	')
    html_out = GuidebookRoffToHTML(center_to_table(src)).convert()
    html_out = html_out
    args.output.write_text(html_out, encoding="utf-8")
    print(f"Wrote {args.output} ({len(html_out)} bytes)")


if __name__ == "__main__":
    main()