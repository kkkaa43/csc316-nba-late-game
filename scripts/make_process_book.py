"""Create the V1 process-book addendum and append it to the original 24 pages.
Requires reportlab & pymupdf (fitz). Does not modify the supplied original PDF.
"""
import io, math
from pathlib import Path
import fitz
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
P=Path(__file__).resolve().parents[1];OLD=P/'reference/CSC316_Previous_Milestones.pdf';OUTPUT=P/'process_book/CSC316_Updated_Process_Book_V1.pdf'
OUTADD=P/'process_book/Prototype_V1_Addendum.pdf'
try:
    pdfmetrics.registerFont(TTFont('Clear','/usr/share/fonts/truetype/clear-sans/ClearSans-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('ClearBold','/usr/share/fonts/truetype/clear-sans/ClearSans-Bold.ttf'))
except OSError:
    # Portable fallback: process book is also shipped already-rendered.
    pdfmetrics.registerFontFamily('Helvetica',normal='Helvetica',bold='Helvetica-Bold')
    # Alias names are handled by selecting built-in fonts below.
    from reportlab.pdfbase.pdfmetrics import Font
    pdfmetrics.registerFont(Font('Clear','Helvetica','WinAnsiEncoding'))
    pdfmetrics.registerFont(Font('ClearBold','Helvetica-Bold','WinAnsiEncoding'))
W,H=612,792
NAVY='#142438';TERRA='#e67952';TEAL='#319a97';BG='#f6f8fa';MUTE='#677989';LINE='#dde6ec';PALE='#e9f1f5';ORANGE='#ffeddf'
C=None;pn=0

def color(hex): return tuple(int(hex[i:i+2],16)/255 for i in (1,3,5))
def setfill(s): C.setFillColorRGB(*color(s))
def setstroke(s): C.setStrokeColorRGB(*color(s))
def rect(x,y,w,h,fill=BG,stroke=None,r=0):
 setfill(fill);setstroke(stroke or fill)
 if r:C.roundRect(x,H-y-h,w,h,r,fill=1,stroke=int(stroke is not None))
 else:C.rect(x,H-y-h,w,h,fill=1,stroke=int(stroke is not None))
def ln(x1,y1,x2,y2,stroke=LINE,width=1):setstroke(stroke);C.setLineWidth(width);C.line(x1,H-y1,x2,H-y2)
def circle(x,y,r,fill=TEAL,stroke=None):setfill(fill);setstroke(stroke or fill);C.circle(x,H-y,r,stroke=int(stroke is not None),fill=1)
def text(x,y,s,size=11,fill=NAVY,font='Clear',align='left'):
 setfill(fill);C.setFont(font,size)
 if align=='center':C.drawCentredString(x,H-y,s)
 elif align=='right':C.drawRightString(x,H-y,s)
 else:C.drawString(x,H-y,s)
def para(x,y,s,width=480,size=10.3,fill=MUTE,leading=16,font='Clear'):
 for line in simpleSplit(s,font,size,width): text(x,y,line,size,fill,font);y+=leading
 return y

def section(y,num,headline,lead=None):
 text(43,y,num,9,TERRA,'ClearBold');text(43,y+33,headline,26,NAVY,'ClearBold')
 return para(43,y+58,lead,520,10.2,MUTE,15) if lead else y+56

def top(kicker,title):
 global pn
 pn+=1;rect(0,0,W,H,'#ffffff');rect(0,0,W,12,NAVY)
 text(43,46,'DESPERATION / METER',11,NAVY,'ClearBold');text(570,46,'PROTOTYPE V1',9,TERRA,'ClearBold','right')
 ln(43,59,569,59)
 text(43,88,kicker.upper(),9,TERRA,'ClearBold');text(43,122,title,24,NAVY,'ClearBold')
 ln(43,738,569,738);text(43,759,'CSC316  |  NBA fourth-quarter data story',9,MUTE);text(569,759,f'ADDENDUM {pn:02d}',9,MUTE,align='right')

def bullet(x,y,title,desc,width=470):
 circle(x+5,y-4,3,TERRA);text(x+18,y,title,11,NAVY,'ClearBold');yy=para(x+18,y+18,desc,width-20,9.7,MUTE,14)
 return yy+10

def mini_header(x,y,title,subtitle=''):
 text(x,y,title,14,NAVY,'ClearBold')
 if subtitle: text(x,y+18,subtitle,9,MUTE)

buffer=io.BytesIO();C=canvas.Canvas(buffer,pagesize=(W,H),pageCompression=1)
# 1
rect(0,0,W,H,NAVY);rect(0,0,9,H,TERRA)
for r in [145,230,320]:setstroke('#2b4259');C.setLineWidth(1);C.circle(500,H-360,r,fill=0,stroke=1)
text(46,79,'CSC316  /  PROTOTYPE V1',11,'#f4b28f','ClearBold')
text(46,174,'Desperation',42,'#ffffff','ClearBold');text(46,222,'/ Meter',42,'#f58d62','ClearBold')
text(46,280,'NBA late-game tactics and comeback outcomes',15,'#c5d5e4')
para(46,332,'A structured, interactive website prototype. Includes the previous twenty-four pages of milestones plus new documentation for implementation, data engineering, innovative view design, and the next iteration.',445,12,'#d5e2ec',20)
rect(44,466,515,132,'#21374d',None,10)
text(64,495,'PROTOTYPE STATUS / 8 NOVEMBER 2026',10,'#f1ac88','ClearBold')
para(64,521,'D3 visualizations and site layout implemented. Source-aware Python cleaning and aggregation code implemented with synthetic unit tests. Full-season real data import remains unverified because the source release could not be downloaded in this environment.',468,10.5,'#f0f5fa',17)
text(46,654,'PROCESS BOOK / UPDATED',11,'#f0f3f7','ClearBold')
text(46,681,'Original milestones preserved verbatim; V1 addendum follows.',10,'#b8c8d5')
C.showPage()
# 2
pn+=1;top('Submission & contributors','Submission inventory')
para(43,151,'The original process book lists the three students below. The active contributor list for this specific V1 submission must be confirmed by the team before grading.',520,10.3,MUTE,16)
rect(43,198,526,38,NAVY,None,5);text(57,222,'STUDENT',10,'#ffffff','ClearBold');text(278,222,'V1 CONTRIBUTION VERIFICATION',10,'#ffffff','ClearBold')
for idx,(name,role) in enumerate([('Jinhao Zhang','Original sketches J1/J2/J3/J4/J5; V1 coordinator to confirm'),('Herui Zhang','Original sketches H1-H5; V1 work to confirm'),('Shiyuan Lyu','Original sketches S1-S5; V1 work to confirm')]):
 y=240+idx*59;rect(43,y,526,56,'#f5f8fa' if idx%2==0 else '#ffffff',LINE,4);text(57,y+23,name,11,NAVY,'ClearBold');text(278,y+22,'[ ] Actively contributed to V1',9,MUTE);para(278,y+40,role,276,8.2,MUTE,10)
section(445,'WHAT IS IN THE ZIP?','Evidence & deliverables')
for i,(h,s) in enumerate([
 ('Working source','SvelteKit, SVG/D3 components, page and responsive CSS.'),
 ('Three functioning D3 renderers','J1 line graph, J4-R custom glyph map, and a supplemental comeback heatmap.'),
 ('Reproducible data scripts','Source download, cleaning, exposure windows, state outcomes, CSV exports, provenance.'),
 ('Updated process book','Original 24 pages plus this V1 design and implementation addendum.')]):
 y=500+i*48;circle(55,y-4,7,TEAL);text(55,y-.5,str(i+1),8,'#ffffff','ClearBold','center');text(72,y,h,10,NAVY,'ClearBold');text(72,y+16,s,8.9,MUTE)
C.showPage()
# 3
pn+=1;top('Pipeline','Data provenance and computation')
para(43,148,'Source: SportsDataverse / hoopR, ESPN NBA play-by-play 2024-25 season release. This updates the original milestone plan that named NBA.com directly.',525,10,MUTE,16)
steps=[('01','DOWNLOAD','play_by_play_2025.parquet'),('02','VALIDATE','Required columns, regular-season games'),('03','CLEAN','Clock, ordering, pre-shot scores, event types'),('04','DERIVE','Trailing state and eventual game outcome'),('05','AGGREGATE','3PA share, exposure rates, comeback fractions'),('06','EXPORT','Static CSV files + SHA256 provenance')]
for i,(number,name,desc) in enumerate(steps):
 y=197+i*61;rect(43,y,526,51,'#f2f7f9',LINE,7);rect(51,y+8,35,35,NAVY,None,6);text(68,y+30,number,11,'#ffffff','ClearBold','center');text(99,y+20,name,9,TEAL,'ClearBold');text(99,y+38,desc,10,NAVY)
 if i<5:ln(68,y+51,68,y+60,TERRA,2)
rect(43,580,526,125,ORANGE,None,7)
text(59,605,'CRITICAL CALCULATION RULES',10,'#9d5439','ClearBold')
para(59,626,'Shot strategy is grouped by the score BEFORE a play (a made basket must not change its own classification). Comeback rate is a proportion of unique team-games per state cell. Shooting/turnover frequencies divide by real seconds spent trailing in that cell, using adjacent event clocks.',492,9.7,'#6b5347',15)
C.showPage()
# 4
pn+=1;top('Implementation','Website architecture and functionality')
text(43,157,'SITE STRUCTURE',10,TEAL,'ClearBold')
sections=[('HERO','Question and example game clock'),('01','Same deficit / different time'),('02','Historical comeback matrix'),('03','Three-point selection (J1)'),('04','Tactical fingerprint (J4-R)'),('05','Future visualization drafts'),('06','Main message and methodology')]
for i,(t,s) in enumerate(sections):
 y=177+i*48;rect(43,y,526,39,'#f4f7f9' if i%2==0 else '#ffffff',LINE,5);rect(55,y+8,54,23,NAVY,None,4);text(82,y+23,t,9,'#ffffff','ClearBold','center');text(127,y+25,s,10,NAVY)
text(43,565,'D3 / SVELTE DESIGN PATTERN',10,TEAL,'ClearBold')
flow=[('d3.csv','fetch derived tables'),('$state','store chart data'),('$effect','redraw when data updates'),('SVG','scales, glyphs, markers')]
for i,(k,v) in enumerate(flow):
 x=43+i*134;rect(x,592,119,73,'#f2f7f9',LINE,7);text(x+60,617,k,12,NAVY,'ClearBold','center');text(x+60,637,v,8,MUTE,align='center')
 if i<3:text(x+123,630,'>',13,TERRA,'ClearBold')
para(43,690,'The responsive page uses chart cards, anchors, chart legends, hover details, a glyph selection panel, and placeholders for three future views.',520,9.2,MUTE,14)
C.showPage()
# 5
pn+=1;top('Implemented visualization J1','Three-point shot selection')
para(43,151,'Research question: How does the fraction of field-goal attempts that are three-pointers change with deficit and remaining time?',520,10,MUTE,16)
rect(43,200,526,300,'#f6f9fb',LINE,9)
# Stylized diagram, deliberately without numeric findings
for j,frac in enumerate([0,.25,.5,.75,1]):
 y=459-j*225;ln(88,y,537,y,'#d8e2e8',.8);text(78,y+4,f'{int(frac*100)}%',9,MUTE,align='right')
for i,s in enumerate(['1-3','4-6','7-10','11+']):text(126+i*127,479,s,10,MUTE,align='center')
for j,(col,b) in enumerate([(TEAL,[.24,.30,.35,.41]),(TERRA,[.32,.45,.53,.65]),('#7898b2',[.22,.23,.28,.33])]):
 C.setStrokeColorRGB(*color(col));C.setLineWidth(2.7)
 pts=[(126+i*127,459-v*225) for i,v in enumerate(b)]
 for i in range(3):ln(*pts[i],*pts[i+1],stroke=col,width=2.7)
 for x,y in pts:circle(x,y,4,col)
text(85,224,'DESIGN-ONLY LINE CHART MOCKUP / NOT ANALYSIS RESULTS',9,TERRA,'ClearBold')
text(88,518,'X: deficit  |  Y: three-point share of FGA  |  Color: clock bands',9,MUTE)
text(43,551,'IMPLEMENTED TECHNIQUES',10,TEAL,'ClearBold')
y=575
for h,s in [('Data binding','d3.csv + d3.autoType read the generated aggregation table.'),('Visual encoding','D3 scalePoint x, linear percentage y, color-coded time-series lines.'),('Interaction','Highlight one clock window, hover markers for percentage and shot count.')]:y=bullet(45,y,h,s,500)
C.showPage()
# 6
pn+=1;top('Innovative visualization J4-R','Tactical Fingerprint Map')
para(43,150,'Novel design from Milestone 4: a 4 x 4 state grid of custom triangular radial glyphs. A separate outer arc encodes the historical comeback rate.',525,10,MUTE,16)
rect(43,197,526,305,'#f7faf9',LINE,9)
# grid illustrative glyphs
for i in range(4):
 text(92,257+i*59,['1-3','4-6','7-10','11+'][i],9,MUTE,align='right')
 for j in range(4):
  cx=133+j*116;cy=246+i*59
  rect(cx-39,cy-27,81,53,'#ffffff','#e5ecee',7)
  for rr in [13,19]:setstroke('#d7e4e5');C.setLineWidth(.7);C.circle(cx,H-cy,rr,stroke=1,fill=0)
  radii=[11+3*i+2*j,13+2*j,9+2*i]
  ang=[-math.pi/2,math.pi/6,5*math.pi/6]
  pts=[(cx+r*math.cos(a),cy+r*math.sin(a)) for r,a in zip(radii,ang)]
  path=C.beginPath();path.moveTo(pts[0][0],H-pts[0][1]);
  for xx,yy in pts[1:]:path.lineTo(xx,H-yy)
  path.close();setfill('#b6ded8');setstroke(TEAL);C.drawPath(path,stroke=1,fill=1)
  setstroke(TERRA);C.setLineWidth(2.1)
  C.arc(cx-24,H-cy-24,cx+24,H-cy+24,startAng=105,extent=220-11*i-13*j)
for j,t in enumerate(['9-12','6-9','3-6','0-3']):text(133+j*116,215,t+' min',9,NAVY,'ClearBold','center')
text(43,531,'CHANNEL MAPPING',10,TEAL,'ClearBold')
items=[('TOP SPOKE','Three-point attempt share'),('BOTTOM LEFT','Field-goal attempts per exposed minute'),('BOTTOM RIGHT','Turnovers per exposed minute'),('OUTER ARC','Share of trailing game states that eventually won')]
for i,(a,b) in enumerate(items):
 y=554+32*i;circle(49,y-4,4,[TERRA,TEAL,'#777ec5',TERRA][i]);text(60,y,a,9,NAVY,'ClearBold');text(194,y,b,9.1,MUTE)
text(43,696,'Interaction: click a cell for raw units, observations, and historical rate.',9.4,MUTE)
C.showPage()
# 7
pn+=1;top('Narrative design','Storyboard and page flow')
para(43,147,'The final page order follows the submitted Milestone 6 premise: urgency can be mistaken for momentum when probability of winning is shrinking.',526,10,MUTE,16)
labels=[('HOOK','Is the same deficit equally recoverable?'),('ODDS','Comeback matrix by deficit and clock'),('TACTICS 1','3PT attempt share across time'),('TACTICS 2','Custom multi-indicator fingerprint'),('INTERPRET','Urgency is not necessarily momentum'),('NEXT','S4 / J2 / H4 extension drafts')]
for i,(name,body) in enumerate(labels):
 y=198+i*79;bg=['#eef4f7','#f3f7f8','#fff3eb','#ecf7f5','#fcece4','#f1f2f9'][i]
 rect(67,y,478,61,bg,LINE,9);rect(75,y+11,89,38,NAVY,None,5);text(119,y+34,name,9,'#ffffff','ClearBold','center');para(183,y+25,body,340,10,NAVY,14)
 if i<5:ln(306,y+61,306,y+79,TERRA,2)
text(43,707,'Principle used: one clear idea per transition (CSC316 storyboard lecture).',9,MUTE)
C.showPage()
# 8
pn+=1;top('Drafts not yet implemented','Three visualization concepts')
# three cards
items=[('S4  /  ACCURACY HEATMAP','Do late-game tactics sacrifice precision?','X: clock band  |  Y: deficit band  |  Color: FG%','Cell details: FGM / FGA, confidence and n warnings'),
('J2  /  PACE VS COMEBACK','Does taking shots faster correlate with wins?','X: change in FGA per minute  |  Y: comeback rate','Dots/bubbles by game-state strata and number of games'),
('H4  /  TEAM COMPARISON','Which teams differ under the same conditions?','Horizontal bars: team-level 3PA share','Select common deficit/time; show league reference and n')]
for i,(h,q,enc,interaction) in enumerate(items):
 y=176+i*176;rect(43,y,526,157,'#f6f9fb',LINE,9);text(60,y+29,h,11,TERRA,'ClearBold');text(60,y+52,q,13,NAVY,'ClearBold');
 para(60,y+76,enc,475,10,MUTE,15);para(60,y+98,interaction,475,9.4,MUTE,15)
 if i==0:
  for a in range(2):
   for b in range(7):rect(61+b*25,y+121+a*13,21,10,[TEAL,'#d2b7a5','#ea8664'][((a*7+b)%3)])
 elif i==1:
  for z in range(8):circle(66+z*26,y+135-(z%3)*6,2.9,TERRA)
 else:
  for z in range(4):rect(63,y+116+z*9,120-z*23,6,TEAL)
text(43,715,'All charts above are revised design drafts, not implemented visualizations.',9.2,MUTE)
C.showPage()
# 9
pn+=1;top('Verification & next steps','Honest progress assessment')
statuses=[('Website layout','DONE','Hero, sections, navigation, placeholders, source notes.'),('D3 chart implementation','DONE','Three CSV-loading visualizations including custom glyphs.'),('Pipeline code','IMPLEMENTED','Python download, validation, pre-event transformation, aggregation.'),('Pipeline on full real season','NOT YET VERIFIED','Network restriction prevented fetching large original parquet in this build.'),('V1 active-member list','NEEDS TEAM CHECK','Roster is known; verify individual prototype contribution.'),('Design drafts','DONE','S4, J2, H4 documented and displayed as placeholders.')]
for i,(title,status,detail) in enumerate(statuses):
 y=166+i*69;rect(43,y,526,59,'#f7fafb',LINE,7);text(56,y+22,title,10.5,NAVY,'ClearBold');text(556,y+21,status,8.5,TEAL if status=='DONE' else TERRA,'ClearBold','right');text(56,y+41,detail,9,MUTE)
rect(43,606,526,105,ORANGE,None,8);text(58,632,'BEFORE FINAL SUBMISSION',10,'#ad5d3c','ClearBold')
para(58,652,'Run: pip install -r scripts/requirements.txt; python scripts/build_data.py --season 2025; python -m unittest discover -s tests -v; npm install; npm run check; npm run build. Inspect sample sizes, real-data metadata, chart legibility, and participant credits. Only then remove the pending-status note.',490,9.3,'#715648',15)
C.showPage()
C.save();buffer.seek(0);OUTADD.write_bytes(buffer.getvalue())
orig=fitz.open(OLD);add=fitz.open(OUTADD);total=fitz.open();total.insert_pdf(orig);total.insert_pdf(add)
# PDF metadata
meta={'title':'CSC316 NBA Late-Game Strategy | Process Book Updated Prototype V1', 'author':'CSC316 project group', 'subject':'Original milestones 1-6 and Prototype V1 implementation addendum'}
total.set_metadata(meta)
OUTPUT.parent.mkdir(parents=True,exist_ok=True);total.save(OUTPUT,garbage=3,deflate=True)
print(f'Created {OUTPUT} ({len(total)} pages: {len(orig)} original + {len(add)} addendum)')
