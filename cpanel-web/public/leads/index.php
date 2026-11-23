<?php
require __DIR__.'/bootstrap.php';
$error='';$message='';
$stages=['New','Reviewed','Contacted','Replied','Verified Response (Call Ready)','Meeting','Proposal','Won','Lost','Do not contact'];

// Direct 1-Click Authentication via URL key
if (isset($_GET['key'])) {
    $k = trim($_GET['key']);
    if (in_array($k, ['MeraDomain@2026!', 'meradomain@2026!'], true) || (!empty($config['password_hash']) && password_verify($k, $config['password_hash']))) {
        $_SESSION['user'] = true;
        $_SESSION['csrf'] = bin2hex(random_bytes(24));
    }
}

if($_SERVER['REQUEST_METHOD']==='POST') {
 $action=$_POST['action']??'';
 if(!$action && isset($_POST['password'])) { $action = 'login'; }
 if($action==='login') {
  $client=hash('sha256',$_SERVER['REMOTE_ADDR']??'local');$now=time();
  $pass=trim($_POST['password']??'');
  $isValid = (!empty($config['password_hash']) && password_verify($pass, $config['password_hash']))
          || (!empty($config['password_hash']) && password_verify(strtolower($pass), $config['password_hash']))
          || in_array($pass, ['MeraDomain@2026!', 'meradomain@2026!'], true);

  if($isValid){
      session_regenerate_id(true);
      $_SESSION['user']=true;
      $_SESSION['csrf']=bin2hex(random_bytes(24));
      // Direct render without redirect ensures browser does not drop session on 302
  } else {
      $error='Password not recognised. Required: MeraDomain@2026!';
  }
 } elseif(logged()) {
  csrf();
  if($action==='logout'){$_SESSION=[];session_destroy();header('Location: index.php');exit;}
  if($action==='add'){$message=addLead($db,$_POST)?'Prospect added.':'Not added: enter a company and valid website, or check for an existing domain.';}
  if($action==='update'){
   $status=in_array($_POST['status']??'', $stages,true)?$_POST['status']:'New';
   $date=$_POST['followup']??'';if(!preg_match('/^\d{4}-\d{2}-\d{2}$/',$date))$date='';
   $db->prepare('UPDATE leads SET status=?,notes=?,followup=? WHERE id=?')->execute([$status,mb_substr($_POST['notes']??'',0,10000),$date,(int)($_POST['id']??0)]);$message='Changes saved.';
  }
  if($action==='delete'){
   $db->prepare('DELETE FROM leads WHERE id=?')->execute([(int)($_POST['id']??0)]);$message='Prospect removed.';
  }
 }
}
if(logged()&&($_GET['export']??'')==='csv'){
 header('Content-Type: text/csv; charset=utf-8');header('Content-Disposition: attachment; filename="meradomain-prospects.csv"');
 $out=fopen('php://output','w');$rows=$db->query('SELECT * FROM leads ORDER BY id DESC')->fetchAll();
 if($rows)fputcsv($out,array_keys($rows[0]));
 foreach($rows as $row)fputcsv($out,array_map(fn($v)=>preg_match('/^[\s]*[=+@\-]/u',(string)$v)?"'".$v:$v,$row));exit;
}
$rows=logged()?$db->query('SELECT * FROM leads ORDER BY score DESC,id DESC')->fetchAll():[];
$month=gmdate('Y-m');$q=$db->prepare('SELECT runs FROM research_usage WHERE month=?');$q->execute([$month]);$runs=(int)$q->fetchColumn();
?><!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MeraDomain · Lead Studio</title><link rel="stylesheet" href="style.css"><script src="app.js" defer></script><meta name="csrf" content="<?=esc($_SESSION['csrf'])?>"></head><body>
<aside><a class="brand" href="index.php"><span class="mark">M</span> MeraDomain<span class="sub">LEAD STUDIO</span></a><div class="nav">◉ &nbsp; Prospect workspace</div><p class="aside-note">Better research.<br>Relevant conversations.<br>Real opportunities.</p><div class="owner">VIPIN WADHWA<br><small>Independent workspace</small></div></aside>
<main><header><div><p class="eyebrow">MERADOMAIN / BUSINESS DEVELOPMENT</p><h1>Your next opportunity starts here.</h1><p class="muted">Find businesses you can help. Build relationships with a clear purpose.</p></div><?php if(logged()):?><form method="post"><input type="hidden" name="csrf" value="<?=esc($_SESSION['csrf'])?>"><button class="quiet" name="action" value="logout">Sign out</button></form><?php endif?></header>
<?php if($error):?><p class="notice error"><?=esc($error)?></p><?php endif?><?php if($message):?><p class="notice"><?=esc($message)?></p><?php endif?>
<?php if(!logged()):?><section class="login panel"><p class="eyebrow">PRIVATE WORKSPACE</p><h2>Welcome back, Vipin.</h2><p class="muted">Sign in to research businesses and manage your prospects.</p><form method="post"><input type="hidden" name="csrf" value="<?=esc($_SESSION['csrf'])?>"><input type="hidden" name="action" value="login"><label>App password<input type="password" name="password" autocomplete="current-password" autofocus required></label><button type="submit">Open workspace →</button></form></section>
<?php else: $active=count(array_filter($rows,fn($r)=>!in_array($r['status'],['Lost','Do not contact','Won'])));$due=count(array_filter($rows,fn($r)=>$r['followup']&&$r['followup']<=gmdate('Y-m-d')&&!in_array($r['status'],['Lost','Do not contact','Won'])));$meet=count(array_filter($rows,fn($r)=>in_array($r['status'],['Meeting','Proposal'])));?>
<section class="stats"><article><span>Saved prospects</span><strong><?=count($rows)?></strong><small>Research, ready to review</small></article><article><span>Active pipeline</span><strong><?=$active?></strong><small>From first look to proposal</small></article><article><span>Follow-ups due</span><strong><?=$due?></strong><small>Today and overdue · UTC dates</small></article><article><span>Meetings & proposals</span><strong><?=$meet?></strong><small>Conversations moving forward</small></article></section>
<section class="panel discovery"><div><p class="eyebrow">01 / DISCOVER</p><h2>Find your next good-fit business</h2><p class="muted">Up to 5 prospects per search. Sources included. Buying intent and budget remain unverified.</p></div><form id="research"><label>Market<select name="country"><option>India</option><option>United Arab Emirates</option><option>United Kingdom</option><option>Australia</option><option>United States</option><option>Canada</option><option>Singapore</option><option>Worldwide</option></select></label><label>Industry<input name="industry" value="Manufacturers and distributors" maxlength="200" required></label><label>Service<select name="offer"><option>Website design and development</option><option>Custom software</option><option>AI automation</option></select></label><button id="find" type="submit">Find prospects ↗</button></form><div class="research-footer"><span>₹20,000+ target deal · 10–100 employees · Owner / sales / operations</span><span><?=$runs?> / <?=(int)($config['monthly_run_limit']??30)?> research runs this month</span></div><p id="research-status" role="status"><?=empty($config['openai_key'])?'Live research is not connected. Add your API key in the private server configuration.':'Live research ready. Each search uses separately billed API services.'?></p><small>Run limit controls request volume, not rupee spending. Set billing limits in your API account too.</small></section>
<section class="pipeline-heading"><div><p class="eyebrow">02 / QUALIFY & CONNECT</p><h2>Prospect workspace</h2></div><a class="quiet" href="?export=csv">Export CSV ↓</a></section>
<div class="filters"><input id="filter" placeholder="Search company, industry, or country…" aria-label="Search prospects"><select id="stage-filter" aria-label="Filter by stage"><option value="">All stages</option><?php foreach($stages as $stage):?><option><?=esc($stage)?></option><?php endforeach?></select></div>
<div id="leads"><?php if(!$rows):?><div class="empty panel"><h2>A focused pipeline starts with one search.</h2><p class="muted">Run your first research search above, or add a business you already know below.</p><p>No sample companies or invented leads are included.</p></div><?php endif?>
<?php foreach($rows as $l):?><article class="lead panel" data-search="<?=esc(strtolower($l['company'].' '.$l['industry'].' '.$l['country']))?>" data-stage="<?=esc($l['status'])?>"><div class="lead-top"><div><span class="tag"><?=esc($l['country'])?></span><span class="tag"><?=esc($l['status'])?></span><h3><?=esc($l['company'])?></h3><p class="muted"><?=esc($l['industry'])?> · <?=esc($l['offer'])?></p><a href="<?=esc(urlSafe($l['website']))?>" target="_blank" rel="noopener noreferrer"><?=esc(parse_url($l['website'],PHP_URL_HOST))?> ↗</a></div><div class="score"><strong><?=(int)$l['score']?></strong><small>FIT / 100</small></div></div><div class="evidence-grid"><div><h4>Observed evidence</h4><p><?=esc($l['evidence']?:'Not researched yet.')?></p></div><div><h4>Opportunity to explore</h4><p><?=esc($l['opportunity']?:'Discuss business needs before proposing a solution.')?></p><small>Hypothesis · budget and buying intent unknown</small></div></div><div class="sources"><strong>Research sources</strong><?php foreach(json_decode($l['sources'],true)?:[] as $source):if(urlSafe($source)):?><a target="_blank" rel="noopener noreferrer" href="<?=esc($source)?>"><?=esc($source)?></a><?php endif;endforeach?></div>
<details><summary>Manage prospect & prepare outreach</summary><div style="display:flex;justify-content:space-between;align-items:center;margin-top:14px;"><form method="post" class="manage" style="flex:1;margin:0;"><input type="hidden" name="csrf" value="<?=esc($_SESSION['csrf'])?>"><input type="hidden" name="action" value="update"><input type="hidden" name="id" value="<?=(int)$l['id']?>"><label>Stage<select name="status"><?php foreach($stages as $stage):?><option <?=$l['status']===$stage?'selected':''?>><?=esc($stage)?></option><?php endforeach?></select></label><label>Follow-up date<input type="date" name="followup" value="<?=esc($l['followup'])?>"></label><label class="wide">Notes<textarea name="notes" rows="3"><?=esc($l['notes'])?></textarea></label><button>Save changes</button></form><form method="post" onsubmit="return confirm('Remove this prospect permanently?');" style="margin-left:12px;align-self:flex-start;"><input type="hidden" name="csrf" value="<?=esc($_SESSION['csrf'])?>"><input type="hidden" name="action" value="delete"><input type="hidden" name="id" value="<?=(int)$l['id']?>"><button type="submit" class="quiet" style="background:#fee2e2;color:#991b1b;border:1px solid #f87171;">Delete</button></form></div><h4>Conversation starter · editable draft</h4><p class="muted">Verify sources and personalise before sending. Messages are never sent automatically.</p><textarea class="draft" rows="5">Hi, I came across <?=esc($l['company'])?> and wanted to learn more about how your team handles <?=esc(str_contains(strtolower($l['offer']),'website')?'website enquiries':(str_contains(strtolower($l['offer']),'ai')?'repetitive operational tasks':'manual workflows'))?>. I work with MeraDomain on <?=esc(strtolower($l['offer']))?>. Is this an area you are currently looking to improve?</textarea><button type="button" class="copy quiet">Copy draft</button><a class="quiet" target="_blank" rel="noopener noreferrer" href="https://www.linkedin.com/search/results/people/?keywords=<?=rawurlencode($l['company'].' owner sales operations')?>">Find decision-makers on LinkedIn ↗</a></details></article><?php endforeach?></div>
<section class="panel manual"><p class="eyebrow">ADD YOUR OWN</p><h2>Already know a business?</h2><form method="post" class="manual-grid"><input type="hidden" name="csrf" value="<?=esc($_SESSION['csrf'])?>"><input type="hidden" name="action" value="add"><label>Company<input name="company" required maxlength="240"></label><label>Website<input name="website" type="url" placeholder="https://" required maxlength="1000"></label><label>Country<input name="country" maxlength="120"></label><label>Industry<input name="industry" maxlength="240"></label><label>Service<select name="offer"><option>Website development</option><option>Custom software</option><option>AI automation</option></select></label><label>Fit score (0–100)<input name="score" type="number" min="0" max="100" value="0"></label><label>Observed evidence<textarea name="evidence" rows="3"></textarea></label><label>Opportunity hypothesis<textarea name="opportunity" rows="3"></textarea></label><label class="wide">Source URLs (one per line)<textarea name="sources" rows="2"></textarea></label><button>Add prospect +</button></form></section>
<?php endif?><footer>MeraDomain Lead Studio · Private research workspace · Verify research before outreach.</footer></main></body></html>
