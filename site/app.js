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
