# Builds the presentation via PowerPoint COM. Run: powershell -File scripts\build_ppt.ps1
param([string]$Out = "$PSScriptRoot\..\ECommerce_Data_Quality_Soda_Presentation.pptx",
      [string]$PreviewDir = "")

function C([string]$h){ [Convert]::ToInt32($h.Substring(0,2),16) + 256*[Convert]::ToInt32($h.Substring(2,2),16) + 65536*[Convert]::ToInt32($h.Substring(4,2),16) }
$BG=C "F4F2EE"; $DARK=C "23242D"; $TERRA=C "C97B5A"; $TERRA2=C "D98B6A"; $TINT=C "E8E2DB"
$BORDER=C "D9B8A6"; $MUTED=C "6B6A68"; $WHITE=C "FFFFFF"; $CODEFG=C "E8E2DB"
$FONT="Segoe UI"; $MONO="Consolas"

$ppt = New-Object -ComObject PowerPoint.Application
$pres = $ppt.Presentations.Add(-1)
$pres.PageSetup.SlideWidth = 960; $pres.PageSetup.SlideHeight = 540
$script:n = 0

function Box($s,$x,$y,$w,$h,$fill,$line=$null,$round=$true){
  $shp = $s.Shapes.AddShape($(if($round){5}else{1}),$x,$y,$w,$h)
  if($round){ $shp.Adjustments.Item(1) = [single](4.0 / [Math]::Min($w,$h)) }
  $shp.Fill.ForeColor.RGB = $fill; $shp.Shadow.Visible = 0
  if($line -ne $null){ $shp.Line.ForeColor.RGB = $line; $shp.Line.Weight = 0.75 } else { $shp.Line.Visible = 0 }
  return $shp
}
function Txt($s,$x,$y,$w,$h,[string]$text,$size,$bold,$color,$align=1,$anchor=1,$font=$FONT,$margin=0){
  $t = $s.Shapes.AddTextbox(1,$x,$y,$w,$h)
  $f = $t.TextFrame; $f.WordWrap = -1; $f.AutoSize = 0
  $f.MarginLeft=$margin; $f.MarginRight=$margin; $f.MarginTop=$margin; $f.MarginBottom=$margin
  $f.VerticalAnchor = $anchor
  $t.Height = $h
  $r = $f.TextRange; $r.Text = $text
  $r.Font.Name=$font; $r.Font.Size=$size; $r.Font.Bold=$(if($bold){-1}else{0}); $r.Font.Color.RGB=$color
  $r.ParagraphFormat.Alignment=$align
  return $t
}
function BoxText($s,$x,$y,$w,$h,$fill,[string]$text,$size,$color,$bold=$true,$align=2,$line=$null){
  $b = Box $s $x $y $w $h $fill $line
  $f=$b.TextFrame; $f.WordWrap=-1; $f.MarginLeft=10; $f.MarginRight=10; $f.MarginTop=4; $f.MarginBottom=4; $f.VerticalAnchor=3
  $r=$f.TextRange; $r.Text=$text; $r.Font.Name=$FONT; $r.Font.Size=$size; $r.Font.Bold=$(if($bold){-1}else{0}); $r.Font.Color.RGB=$color; $r.ParagraphFormat.Alignment=$align
  return $b
}
function Bullets($s,$x,$y,$w,$h,[string[]]$items,$size,$gap=8){
  $t = Txt $s $x $y $w $h ($items -join "`r") $size $false $DARK
  $p = $t.TextFrame.TextRange.ParagraphFormat
  $p.Bullet.Visible=-1; $p.Bullet.Character=8226; $p.Bullet.Font.Color.RGB=$TERRA
  $p.LineRuleAfter=0; $p.SpaceAfter=$gap
  $t.TextFrame.Ruler.Levels.Item(1).FirstMargin=0; $t.TextFrame.Ruler.Levels.Item(1).LeftMargin=16
  return $t
}
function Code($s,$x,$y,$w,$h,[string]$code,$size=11.5){
  $b = Box $s $x $y $w $h $DARK
  $f=$b.TextFrame; $f.WordWrap=-1; $f.MarginLeft=14; $f.MarginRight=10; $f.MarginTop=12; $f.MarginBottom=8; $f.VerticalAnchor=1
  $r=$f.TextRange; $r.Text = ($code.TrimEnd() -replace "`r?`n","`r")
  $r.Font.Name=$MONO; $r.Font.Size=[single]$size; $r.Font.Color.RGB=$CODEFG; $r.Font.Bold=0; $r.ParagraphFormat.Alignment=1
  for($i=1;$i -le $r.Paragraphs().Count;$i++){
    $p=$r.Paragraphs($i); $txt=$p.Text; $idx=$txt.IndexOf('#')
    if($idx -ge 0){ $p.Characters($idx+1, $txt.TrimEnd("`r").Length-$idx).Font.Color.RGB=$TERRA2 }
  }
  return $b
}
function Arrow($s,$x1,$y1,$x2,$y2){
  $l=$s.Shapes.AddLine($x1,$y1,$x2,$y2); $l.Line.ForeColor.RGB=$TERRA; $l.Line.Weight=1.5; $l.Line.EndArrowheadStyle=2
}
function NewSlide($title,$label,$presenter){
  $script:n++
  $s=$pres.Slides.Add($script:n,12)
  $s.FollowMasterBackground=0; $s.Background.Fill.Solid(); $s.Background.Fill.ForeColor.RGB=$BG
  if($title){
    Txt $s 60 24 840 44 $title 30 $true $DARK 1 3 | Out-Null
    Txt $s 60 70 840 16 $label 11 $true $TERRA 1 1 | Out-Null
    $dl=$s.Shapes.AddLine(60,92,900,92); $dl.Line.ForeColor.RGB=$BORDER; $dl.Line.Weight=1
  }
  $l=$s.Shapes.AddLine(60,506,900,506); $l.Line.ForeColor.RGB=(C "C9C5BF"); $l.Line.Weight=0.75
  Txt $s 60 512 400 16 "Data Engineering - Case Study 14" 10 $false $MUTED 1 1 | Out-Null
  if($presenter){ Txt $s 380 512 200 16 "Presenter: $presenter" 10 $true $TERRA 2 1 | Out-Null }
  Txt $s 840 512 60 16 "$($script:n)" 10 $false $MUTED 3 1 | Out-Null
  return $s
}
function Notes($s,[string]$t){ $s.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = $t }
function Table($s,$x,$y,[double[]]$cols,$hdrH,$rowH,[string[]]$hdr,$rows,$size=12,[int[]]$monoCols=@()){
  $cx=$x
  for($c=0;$c -lt $cols.Count;$c++){
    BoxText $s $cx $y ($cols[$c]-2) $hdrH $DARK $hdr[$c] 11 $WHITE $true 1 | Out-Null; $cx+=$cols[$c]
  }
  $ry=$y+$hdrH+3
  foreach($row in $rows){
    $cx=$x
    for($c=0;$c -lt $cols.Count;$c++){
      $b = BoxText $s $cx $ry ($cols[$c]-2) ($rowH-3) $TINT $row[$c] $size $DARK $false 1 $BORDER
      if($monoCols -contains $c){ $b.TextFrame.TextRange.Font.Name=$MONO; $b.TextFrame.TextRange.Font.Size=$size-1 }
      $cx+=$cols[$c]
    }
    $ry+=$rowH
  }
}

# ---------------- Slide 1 : Title ----------------
$s = NewSlide $null $null $null
Txt $s 70 62 760 130 "E-Commerce Data Quality`rusing Soda" 44 $true $DARK 1 1 | Out-Null
$l=$s.Shapes.AddLine(70,200,480,200); $l.Line.ForeColor.RGB=$TERRA; $l.Line.Weight=1
Txt $s 70 214 760 28 "Data Engineering - Practical Case Study 14" 18 $true $TERRA 1 1 | Out-Null
Txt $s 70 280 300 18 "TEAM MEMBERS" 11 $true $MUTED 1 1 | Out-Null
Txt $s 70 304 500 56 "Niharika Singh - 124A8108`rShubham Singh - 124A8109" 17 $true $DARK 1 1 | Out-Null
$labels="DATASET","RULES","VALIDATION","REPORT"; $x=70
for($i=0;$i -lt 4;$i++){
  BoxText $s $x 410 170 46 $(if($i -eq 3){$TERRA}else{$DARK}) $labels[$i] 14 $WHITE | Out-Null
  if($i -lt 3){ Arrow $s ($x+172) 433 ($x+206) 433 }
  $x+=208
}
Notes $s "Dono members apna naam bolein. Tool: Python + Soda Core + DuckDB. Niharika slides 2-4, Shubham slides 5-7."

# ---------------- Slide 2 : Intro ----------------
$s = NewSlide "Why Data Quality Matters in E-Commerce" "THE PROBLEM - ILLUSTRATIVE SCENARIO, SYNTHETIC DATA" "Niharika Singh"
Txt $s 60 108 440 66 "An e-commerce platform records every order, payment and customer. One bad record can silently break everything downstream." 15 $true $DARK | Out-Null
$cards=@(@("NEGATIVE PRICE","Profit report becomes wrong"),@("DUPLICATE ORDER_ID","Same order is counted twice"),@("MISSING CUSTOMER_ID","Delivery cannot be made"),@("INVALID STATUS","Order tracking breaks"))
for($i=0;$i -lt 4;$i++){
  $cx = 60 + ($i % 2) * 225; $cy = 184 + [Math]::Floor($i / 2) * 106
  Box $s $cx $cy 215 96 $TINT $BORDER | Out-Null
  Txt $s ($cx+14) ($cy+12) 190 16 "0$($i+1)" 11 $true $TERRA | Out-Null
  Txt $s ($cx+14) ($cy+30) 190 20 $cards[$i][0] 13 $true $DARK | Out-Null
  Txt $s ($cx+14) ($cy+56) 190 32 $cards[$i][1] 13 $false $MUTED | Out-Null
}
$steps="DATA SOURCES (WEB, APP, PAYMENTS)","BAD RECORDS ENTER","WRONG REVENUE REPORTS","FAILED DELIVERIES","BAD BUSINESS DECISIONS","VALIDATION RULES NEEDED"
$y=108
for($i=0;$i -lt 6;$i++){
  BoxText $s 560 $y 340 34 $(if($i -eq 5){$TERRA}else{$DARK}) $steps[$i] 12 $WHITE | Out-Null
  if($i -lt 5){ Arrow $s 730 ($y+34) 730 ($y+48) }
  $y+=48
}
Txt $s 60 404 840 16 "DISCUSS BEFORE MOVING TO THE SOLUTION" 10 $true $TERRA 2 1 | Out-Null
BoxText $s 60 424 840 62 $DARK "How can we catch bad data automatically, before it reaches reports and decisions?" 18 $WHITE | Out-Null
Notes $s "Niharika: E-commerce data website, app, payment gateway aur warehouse se aata hai - har jagah galti ho sakti hai. Example: price -65,000 aaya toh profit galat; same order_id do baar aaya toh order do baar gina jayega. Lakhon rows manually check nahi ho sakti, isliye data quality framework (Soda) use karte hain. Is practical mein hum dataset banate hain, usme galtiyan daalte hain, aur Soda se pakadte hain."

# ---------------- Slide 3 : Dataset ----------------
$s = NewSlide "Step 1 - Creating the Dataset" "LOAD DATASET  |  scripts/generate_data.py" "Niharika Singh"
$stats=@(@("260","ORDERS"),@("64","CUSTOMERS"),@("14","BAD ROWS"))
$x=60
foreach($st in $stats){
  $b=Box $s $x 108 120 86 $TINT $BORDER
  Txt $s $x 114 120 46 $st[0] 32 $true $TERRA 2 3 | Out-Null
  Txt $s $x 164 120 20 $st[1] 11 $true $DARK 2 1 | Out-Null
  $x+=130
}
Txt $s 60 206 380 16 "SAMPLE ROWS - HIGHLIGHTED = INJECTED ISSUE" 10 $true $MUTED | Out-Null
$cols=@(80,110,70,120); $hd=@("order_id","unit_price","qty","status"); $cx=60
for($c=0;$c -lt 4;$c++){ BoxText $s $cx 226 ($cols[$c]-2) 22 $DARK $hd[$c] 11 $WHITE $true 1 | Out-Null; $cx+=$cols[$c] }
$srows=@(@("O0001","58,200","2","Shipped",-1),@("O9001","-65,000","1","Delivered",1),@("O9002","800","0","Delivered",2),@("O9005","12,000","1","Unknown",3),@("O0001","58,200","2","Shipped",0))
$ry=250
foreach($sr in $srows){
  $cx=60
  for($c=0;$c -lt 4;$c++){
    $bad = ($sr[4] -eq ($c)) -or ($sr[4] -eq 0 -and $c -eq 0)
    if($sr[4] -eq 1){$bad = ($c -eq 1)}; if($sr[4] -eq 2){$bad = ($c -eq 2)}; if($sr[4] -eq 3){$bad = ($c -eq 3)}
    if($sr[4] -eq -1){$bad=$false}
    $b = BoxText $s $cx $ry ($cols[$c]-2) 24 $(if($bad){$TERRA}else{$TINT}) $sr[$c] 12 $(if($bad){$WHITE}else{$DARK}) $bad 1 $(if($bad){$null}else{$BORDER})
    $cx+=$cols[$c]
  }
  $ry+=26
}
Bullets $s 60 384 380 30 @("12 products, 10 cities. seed(42) = same data every run") 12 0 | Out-Null
$code=@'
random.seed(42)   # same data every run

orders.append({
  "order_id": f"O{i:04d}",
  "unit_price": round(base * uniform(0.9, 1.1)),
  "quantity": random.randint(1, 5),
})

bad_rows = [
  {"order_id": "O9001", "unit_price": -65000},  # negative
  {"order_id": "O9002", "quantity": 0},         # zero qty
  {"order_id": "O9003", "customer_id": ""},     # missing
  {"order_id": "O9005", "status": "Unknown"},   # invalid
  {**orders[0], "customer_id": "C050"},         # duplicate
]
random.shuffle(orders)
'@
Code $s 470 108 430 300 $code 12 | Out-Null
BoxText $s 60 428 840 56 $TINT "Output: data/orders.csv (250 clean + 10 bad rows) and data/customers.csv (60 clean + 4 bad rows)" 14 $DARK $true 2 $BORDER | Out-Null
Notes $s "Niharika: Real data confidential hota hai isliye synthetic data banaya. 250 clean orders, price me +-10% variation. Phir 10 bad orders: negative price, zero/negative quantity, missing customer_id/product/date, invalid status, outlier price 999999, future date 2099, duplicate order_id. Customers me 4 bad rows (missing name, missing email, duplicate C001). Last me shuffle taaki bad rows ek jagah na rahein. Seed 42 = har baar same data, demo repeatable."

# ---------------- Slide 4 : DuckDB ----------------
$s = NewSlide "Step 2 - Loading into a Database" "LOAD DATASET  |  scripts/load_duckdb.py + configuration.yml" "Niharika Singh"
$fl="CSV FILES","DUCKDB TABLES","order_details VIEW","SODA SCAN"; $x=60
for($i=0;$i -lt 4;$i++){
  BoxText $s $x 108 192 52 $(if($i -eq 3){$TERRA}else{$DARK}) $fl[$i] 13 $WHITE | Out-Null
  if($i -lt 3){ Arrow $s ($x+194) 134 ($x+220) 134 }
  $x+=216
}
Txt $s 60 174 520 16 "CSV TO TABLES, PLUS A JOINED VIEW" 10 $true $MUTED | Out-Null
Txt $s 600 174 300 16 "HOW SODA CONNECTS" 10 $true $MUTED | Out-Null
$sql=@'
con = duckdb.connect("ecommerce.duckdb")

con.execute("""CREATE TABLE orders AS
  SELECT * FROM read_csv_auto('data/orders.csv')""")

con.execute("""CREATE VIEW order_details AS
  SELECT o.*, c.name AS customer_name,
         o.unit_price * o.quantity AS total_amount
  FROM orders o LEFT JOIN customers c
       USING (customer_id)""")
'@
Code $s 60 194 520 206 $sql 12.5 | Out-Null
$yml=@'
# configuration.yml
data_source ecommerce:
  type: duckdb
  database: ecommerce.duckdb
  read_only: true
  schema_name: main
'@
Code $s 600 194 300 206 $yml 12.5 | Out-Null
BoxText $s 60 420 840 64 $DARK "DuckDB is serverless: no installation, no cloud. read_csv_auto detects column types by itself." 15 $WHITE | Out-Null
Notes $s "Niharika: Soda ko SQL database chahiye scan karne ke liye, isliye CSV ko DuckDB me load kiya. read_csv_auto khud column types detect karta hai. order_details view orders ko customers se join karta hai aur total_amount = price x quantity nikalta hai - isse cross-table checks possible hote hain. configuration.yml Soda ko batata hai kaunsa database use karna hai. HANDOVER: 'Data load ho gaya, DB ready hai. Ab ye data sahi hai ya nahi, ye Shubham batayega.'"

# ---------------- Slide 5 : Rules ----------------
$s = NewSlide "Step 3 - Defining Validation Rules" "checks.yml  |  17 CHECKS ACROSS 5 QUALITY DIMENSIONS" "Shubham Singh"
$rows=@(
 @("Volume","row_count between 200 and 300","Empty or truncated table"),
 @("Completeness","missing_count(customer_id) = 0","Blank required fields"),
 @("Uniqueness","duplicate_count(order_id) = 0","Repeated IDs"),
 @("Validity","invalid_count(status) = 0","Values outside allowed list"),
 @("Range","valid min: 0.01 / max: 500000","Negative or outlier price")
)
Table $s 60 108 @(104,228,148) 28 52 @("DIMENSION","RULE","WHAT IT CATCHES") $rows 12 @(1)
$yaml=@'
checks for orders:
  - row_count between 200 and 300
  - missing_count(customer_id) = 0
  - duplicate_count(order_id) = 0
  - invalid_count(status) = 0:
      valid values: ["Pending",
        "Shipped", "Delivered",
        "Cancelled", "Returned"]
  - invalid_count(unit_price) = 0:
      valid min: 0.01
'@
Code $s 555 108 345 291 $yaml 13 | Out-Null
BoxText $s 60 420 840 64 $DARK "17 checks in total: 12 on orders, 5 on customers. Plain YAML, so even non-programmers can read the rules." 15 $WHITE | Out-Null
Notes $s "Shubham: Ab data load ho gaya, ab rules define karte hain. missing_count(customer_id)=0 ka matlab blank customer_id wali rows zero honi chahiye warna FAIL. Rules business logic se aate hain: price negative nahi, quantity >= 1, status sirf 5 allowed values. Sabse badi baat: YAML hai, business team bhi padh sakti hai."

# ---------------- Slide 6 : Demo ----------------
$s = NewSlide "Step 4 - Running the Scan" "LIVE DEMO  |  scripts/run_demo.py" "Shubham Singh"
$st=@(@("01","GENERATE","Create 260 orders"),@("02","LOAD","Into DuckDB"),@("03","CONNECT","soda test-connection"),@("04","SCAN","Run all 17 checks"))
$x=60
for($i=0;$i -lt 4;$i++){
  $b=Box $s $x 108 195 76 $(if($i -eq 3){$TERRA2}else{$DARK})
  Txt $s ($x+10) 114 40 14 $st[$i][0] 10 $true $(if($i -eq 3){$WHITE}else{$TERRA2}) | Out-Null
  Txt $s $x 128 195 28 $st[$i][1] 15 $true $WHITE 2 1 | Out-Null
  Txt $s $x 156 195 20 $st[$i][2] 11 $false $WHITE 2 1 | Out-Null
  if($i -lt 3){ Arrow $s ($x+197) 146 ($x+218) 146 }
  $x+=215
}
Box $s 60 204 290 214 $TINT $BORDER | Out-Null
Txt $s 76 216 260 18 "WHAT SODA DOES" 12 $true $TERRA | Out-Null
Bullets $s 76 242 262 170 @("Reads checks.yml","Turns each rule into a SQL query","Runs it on the DuckDB tables","Compares result with expected value","Prints PASSED or FAILED per check") 13 7 | Out-Null
$term=@'
PS> python scripts/run_demo.py

# soda scan - illustrative output format
@@ROWS@@
'@
$tl=@(@("orders","missing_count(order_id) = 0","[PASSED]"),@("orders","duplicate_count(order_id) = 0","[FAILED]"),@("orders","invalid_count(status) = 0","[FAILED]"),@("orders","invalid_count(quantity) = 0","[FAILED]"),@("customers","missing_count(email) = 0","[FAILED]"))
$term = $term.Replace("@@ROWS@@", (($tl | ForEach-Object { $_[0].PadRight(11) + $_[1].PadRight(32) + $_[2] }) -join "`n"))
$tb = Code $s 365 204 535 214 $term 12
$tr = $tb.TextFrame.TextRange
for($i=1;$i -le $tr.Paragraphs().Count;$i++){
  $p=$tr.Paragraphs($i); $t=$p.Text
  $k=$t.IndexOf('[PASSED]'); if($k -ge 0){ $p.Characters($k+1,8).Font.Color.RGB=(C "8FB996"); $p.Characters($k+1,8).Font.Bold=-1 }
  $k=$t.IndexOf('[FAILED]'); if($k -ge 0){ $p.Characters($k+1,8).Font.Color.RGB=$TERRA2; $p.Characters($k+1,8).Font.Bold=-1 }
}
Txt $s 60 432 840 16 "ASK THE AUDIENCE BEFORE REVEALING THE ANSWER" 10 $true $TERRA 2 1 | Out-Null
BoxText $s 60 450 840 42 $DARK "Why do some checks FAIL? Because we injected the bad rows on purpose." 16 $WHITE | Out-Null
Notes $s "Shubham: Ek hi command poori pipeline chalata hai. Last step soda scan har rule ko SQL query ki tarah database pe chalata hai. Terminal me har check ke saamne PASS/FAIL aata hai - yehi validation report hai. Demo chalao, phir bolo: kuch checks fail hue, ye intentional hai. Backup: pehle se liya hua terminal screenshot."

# ---------------- Slide 7 : Failures ----------------
$s = NewSlide "Analyzing the Failures" "VALIDATION REPORT  |  WHAT SODA CAUGHT" "Shubham Singh"
$rows=@(
 @("Duplicate order_id","orders","duplicate_count(order_id)"),
 @("Missing customer_id, product, date","orders","missing_count(...)"),
 @("Status = Unknown","orders","invalid_count(status)"),
 @("Price -65,000","orders","unit_price valid min"),
 @("Price 9,99,999","orders","unit_price valid max"),
 @("Quantity 0 and -3","orders","quantity valid min"),
 @("Missing name or email","customers","missing_count(...)"),
 @("Duplicate customer_id C001","customers","duplicate_count(customer_id)")
)
Table $s 60 108 @(244,88,240) 28 37 @("INJECTED PROBLEM","TABLE","RULE THAT CAUGHT IT") $rows 12 @(2)
Box $s 645 108 255 88 $TERRA | Out-Null
Txt $s 645 112 255 50 "12 / 14" 34 $true $WHITE 2 3 | Out-Null
Txt $s 645 162 255 20 "INJECTED ISSUES CAUGHT" 11 $true $WHITE 2 1 | Out-Null
Box $s 645 208 255 128 $TINT $BORDER | Out-Null
Txt $s 661 218 225 16 "NOT CAUGHT YET" 11 $true $TERRA | Out-Null
Bullets $s 661 240 228 92 @("Future dates (2099): no date rule","Unknown customer_id: no cross-table check","Next step: add both rules") 12 3 | Out-Null
Box $s 645 348 255 92 $DARK | Out-Null
Txt $s 661 356 225 16 "TAKEAWAY" 11 $true $TERRA2 | Out-Null
Txt $s 661 376 228 58 "Measurable rules plus automation catch bad data before it reaches reports." 13 $true $WHITE | Out-Null
Txt $s 60 456 840 30 "Failed checks show exactly which column, which rule and how many rows to fix." 14 $true $DARK 2 3 | Out-Null
Notes $s "Shubham: Failure analysis = har fail hue check ko dekhna aur samajhna kya galat hai. Real life me yahan se bad rows quarantine hoti hain, source system fix hota hai ya pipeline rok di jati hai. Limitations honestly batao: future dates aur referential integrity abhi check nahi hote. Closing: Data quality cleaning ka kaam nahi, rules define karke problem ko pehle hi pakadna hai."

$full = [System.IO.Path]::GetFullPath($Out)
$pres.SaveAs($full)
if($PreviewDir){ New-Item -ItemType Directory -Force $PreviewDir | Out-Null; $pres.Export($PreviewDir,"PNG",1600,900) }
$pres.Close(); $ppt.Quit()
"Saved: $full"



