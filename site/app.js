"use strict";
const byId=id=>document.getElementById(id);
const theme=byId("theme");
let selected="dark";
try{selected=localStorage.getItem("portfolio-theme")|| (matchMedia("(prefers-color-scheme: light)").matches?"light":"dark")}catch{}
function setTheme(t){document.documentElement.dataset.theme=t;theme.textContent=t==="dark"?"Light mode":"Dark mode";try{localStorage.setItem("portfolio-theme",t)}catch{}}
setTheme(selected==="light"?"light":"dark");
theme.addEventListener("click",()=>setTheme(document.documentElement.dataset.theme==="dark"?"light":"dark"));
let booking={status:"AVAILABLE",owner:null};
document.querySelectorAll("[data-book]").forEach(button=>button.addEventListener("click",()=>{
 const action=button.dataset.book;let msg="";
 if(action==="reset"){booking={status:"AVAILABLE",owner:null};msg="Reset to available."}
 else if(action==="A"||action==="B"){if(booking.status==="AVAILABLE"){booking={status:"HELD",owner:action};msg="Customer "+action+" acquired the hold."}else{msg="Rejected: slot is already "+booking.status.toLowerCase()+"."}}
 else if(action==="confirm"){if(booking.status==="HELD"){booking.status="CONFIRMED";msg="Confirmed for customer "+booking.owner+"."}else msg="Confirmation requires an active hold."}
 else if(action==="expire"){if(booking.status==="HELD"){booking={status:"AVAILABLE",owner:null};msg="Hold expired. The slot is available again."}else msg="No active hold to expire."}
 byId("booking-state").textContent=booking.status+(booking.owner?" · CUSTOMER "+booking.owner:"");byId("booking-log").textContent=msg;
}));
let phase=0,connected=true;const labels=["queued","sent","delivered","read"];
function renderMessage(note=""){document.querySelectorAll("#message-steps span").forEach((el,i)=>el.classList.toggle("done",i<=phase));byId("message-log").textContent=(connected?"Connected":"Disconnected")+" · "+labels[phase]+(note?" — "+note:"")}
renderMessage();document.querySelectorAll("[data-msg]").forEach(button=>button.addEventListener("click",()=>{const action=button.dataset.msg;let note="";if(action==="reset"){phase=0;connected=true}else if(action==="disconnect")connected=false;else if(action==="connect"){connected=true;note="State retained."}else if(action==="advance"){if(!connected)note="Acknowledgement deferred until reconnect.";else if(phase<3)phase++;else note="Already read."}renderMessage(note)}));
function invoke(){const value=byId("ref").value;const valid=/^BK-[0-9]{4}$/.test(value);byId("tool-result").textContent=JSON.stringify(valid?{ok:true,tool:"booking.lookup",simulation:true,result:{reference:value,status:"demo_only"}}:{ok:false,error:"INVALID_ARGUMENT",expected:"BK- followed by four digits"},null,2)}
byId("tool-form").addEventListener("submit",e=>{e.preventDefault();invoke()});byId("invalid").addEventListener("click",()=>{byId("ref").value="invalid";invoke()});
function show(mode){const terrain=mode==="terrain";byId("activity-graphic").src=terrain?"assets/activity-3d.svg":"assets/activity-heatmap.svg";byId("activity-graphic").alt=terrain?"Isometric public commit activity":"Animated public commit calendar";byId("calendar").setAttribute("aria-pressed",String(!terrain));byId("terrain").setAttribute("aria-pressed",String(terrain))}
byId("calendar").addEventListener("click",()=>show("calendar"));byId("terrain").addEventListener("click",()=>show("terrain"));
async function get(path){const r=await fetch(path);if(!r.ok)throw Error("Snapshot unavailable");return r.json()}
Promise.all([get("assets/github-stats.json"),get("assets/activity.json")]).then(([repos,activity])=>{byId("repo-count").textContent=repos.repositories;byId("commit-count").textContent=activity.total_commits;byId("active-count").textContent=activity.active_days;byId("snapshot").textContent="Public commit window: "+activity.start+" through "+activity.end+" (UTC)."}).catch(()=>{byId("snapshot").textContent="Numeric snapshot could not load; the static charts remain available."});

// Shared skills catalog: accessible, dependency-free filtering.
(function(){
 const root=byId("skill-groups"),search=byId("skill-search"),category=byId("skill-category"),context=byId("skill-context"),status=byId("skill-count");
 if(!root||!search||!category||!context||!status)return;
 const node=(tag,cls,text)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(text!==undefined)el.textContent=text;return el};
 const option=(select,value,label)=>{const el=node("option","",label);el.value=value;select.append(el)};
 function render(data){
  const query=search.value.trim().toLowerCase(), c=category.value, e=context.value;
  const previous=new Map([...root.querySelectorAll("details")].map(el=>[el.dataset.group,el.open]));
  root.replaceChildren();let count=0;
  for(const g of data.categories){
   if(c&&g.id!==c)continue;
   const matching=g.skills.filter(s=>(!e||s.experience===e)&&(!query||[s.name,s.description,g.title,data.experience_labels[s.experience]].join(" ").toLowerCase().includes(query)));
   if(!matching.length)continue;
   count+=matching.length;
   const detail=node("details","skill-group");detail.dataset.group=g.id;detail.open=Boolean(query||c||e)||previous.get(g.id)===true||(!previous.has(g.id)&&g.id==="languages");
   const summary=node("summary","",g.title);summary.append(node("small","",matching.length+" skills"));detail.append(summary,node("p","",g.description));
   const grid=node("div","skill-grid");
   for(const s of matching){
    const card=node("article","skill-card"),icon=node("div","skill-icon"),img=node("img");img.src=s.icon;img.alt="";img.width=36;img.height=36;img.loading="lazy";img.decoding="async";icon.append(img);
    const body=node("div");body.append(node("h3","",s.name),node("p","",s.description),node("span","skill-context",data.experience_labels[s.experience]||s.experience));card.append(icon,body);grid.append(card);
   }
   detail.append(grid);root.append(detail);
  }
  const total=data.categories.reduce((sum,g)=>sum+g.skills.length,0);status.textContent=count+" of "+total+" skills · "+root.querySelectorAll("details").length+" disciplines";
  if(!count)root.append(node("p","skill-empty","No matching skills. Try a different search or reset the filters."));
 }
 get("assets/skills.json").then(data=>{
  if(!Array.isArray(data.categories))throw Error("Invalid skills catalog");
  data.categories.forEach(g=>option(category,g.id,g.title));Object.entries(data.experience_labels).forEach(([key,label])=>option(context,key,label));
  byId("skill-note").textContent=data.note;
  search.addEventListener("input",()=>render(data));category.addEventListener("change",()=>render(data));context.addEventListener("change",()=>render(data));
  byId("skill-reset").addEventListener("click",()=>{search.value="";category.value="";context.value="";render(data);search.focus()});
  byId("skill-expand").addEventListener("click",()=>root.querySelectorAll("details").forEach(el=>el.open=true));
  byId("skill-collapse").addEventListener("click",()=>root.querySelectorAll("details").forEach(el=>el.open=false));
  render(data);
 }).catch(()=>{status.textContent="Skills catalog could not be loaded. The full GitHub reference is available below."});
})();
