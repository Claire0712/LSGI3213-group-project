import fs from 'node:fs/promises';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
import {finalizePresentation,applyPresentationChartFont} from '/Users/zhangshizhuo/.codex/plugins/cache/openai-primary-runtime/presentations/26.905.11957/skills/presentations/container_tools/artifact_tool_utils.mjs';
const root=path.resolve('project');
const contents=JSON.parse(await fs.readFile(path.join(root,'analysis/slides_content.json'),'utf8'));
const p=Presentation.create({slideSize:{width:1280,height:720}});
const cols=['#333333','#E64B35','#4DBBD5','#00A087','#3C5488'];
function text(s,txt,x,y,w,h,size=28,bold=false,color='#263C4B'){
 const sh=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 sh.text=txt;sh.text.style={typeface:'Arial',fontSize:size,bold,color,autoFit:'none'};return sh;
}
function makechart(s,c,position){
 const series=c.series.map((v,i)=>({name:v.name,values:v.y.map(n=>Number(n.toFixed(6))),xValues:v.x?.map(n=>Number(n.toFixed(6))),line:{fill:v.color,width:c.type==='network'?2:3},fill:v.color,marker:{symbol:'none'},...(c.type==='bar'?{points:c.categories.map((_,j)=>({idx:j,fill:cols[j]})),valuesFormatCode:'0.00'}:{})}));
 let type=c.type==='network'?'scatter':c.type;
 const conf={position,series,categories:c.categories,hasLegend:c.type!=='network'&&series.length>1,legend:{position:'bottom',overlay:false,textStyle:{typeface:'Arial',fontSize:23,fill:'#273B49'}},chartFill:'#FFFFFF',plotAreaFill:'#FFFFFF',xAxis:{title:{text:c.xlabel||'',textStyle:{typeface:'Arial',fontSize:23}},min:c.minx,max:c.maxx,textStyle:{typeface:'Arial',fontSize:22},majorGridlines:null},yAxis:{title:{text:c.ylabel||'',textStyle:{typeface:'Arial',fontSize:23}},min:c.miny,max:c.maxy,textStyle:{typeface:'Arial',fontSize:22},majorGridlines:{fill:'#E5EAED',width:1}},...(type==='scatter'?{scatterOptions:{style:'line'}}:{}),...(type==='line'?{lineOptions:{smooth:false}}:{})};
 if(type==='bar'){conf.barOptions={direction:'column',grouping:'clustered',gapWidth:100};conf.yAxis.min=0;conf.yAxis.max=c.max;conf.dataLabels={showValue:true,position:'outEnd',textStyle:{typeface:'Arial',fontSize:24,fill:'#233B4C'}};}
 if(c.type==='network'){conf.xAxis.min=-22;conf.xAxis.max=7;conf.yAxis.min=-12;conf.yAxis.max=8;}
 if(c.ylabel==='Cumulative share'){conf.yAxis.numberFormatCode='0%';conf.yAxis.majorUnit=0.2;}
 if(c.xlabel==='Link ID'){conf.xAxis.majorUnit=1;conf.xAxis.numberFormatCode='0';}
 if(c.xlabel==='Iteration'){conf.xAxis.majorUnit=20;conf.xAxis.numberFormatCode='0';}
 if(c.xlabel==='Hour of day'){conf.xAxis.majorUnit=0.5;conf.xAxis.numberFormatCode='0.0';conf.yAxis.numberFormatCode='0';}
 const chart=s.charts.add(type,conf);applyPresentationChartFont(chart,{fontFamily:'Arial'});
}
for(let i=0;i<contents.length;i++){
 const d=contents[i],s=p.slides.add();s.background.fill='#FFFFFF';
 text(s,d.title,68,i===0?90:42,1140,i===0?165:105,i===0?62:44,true,'#17384E');
 if(d.table){
   const widths=i===4?[200,505,435]:[260,475,405];
   const tab=s.tables.add({rows:d.table.length,columns:d.table[0].length,left:68,top:178,width:1140,height:390,columnWidths:widths,values:d.table});
   for(let r=0;r<d.table.length;r++){
     tab.rows[r].height=65;
     for(let c=0;c<d.table[0].length;c++){
       const cell=tab.getCell(r,c);cell.text.style={typeface:'Arial',fontSize:24,color:'#243C4D',bold:r===0};cell.fill=r===0?'#E8EEF2':'#FFFFFF';
     }
   }
 }else if(d.chart){
   makechart(s,d.chart,d.chart.type==='network'?{left:62,top:175,width:740,height:410}:{left:75,top:165,width:1120,height:450});
   if(d.body)d.body.forEach((line,j)=>text(s,line,840,190+j*94,360,88,26));
 }else if(d.body){
   d.body.forEach((line,j)=>text(s,line,72,(i===0?320:178)+j*(i===0?68:100),1130,i===0?58:86,i===0?28:30));
 }
 if(d.foot)text(s,d.foot,72,633,1110,45,18,false,'#607480');
 text(s,String(i+1).padStart(2,'0'),1174,677,55,24,17,false,'#607480');
 s.speakerNotes.textFrame.setText(`Timing: ${d.seconds} seconds.\n\n${d.notes}\n\nSources: ${d.foot||'Project report and saved MATSim outputs.'}`);
}
const stage=path.join(root,'.build');const candidate=path.join(stage,'candidate.pptx');
await(await PresentationFile.exportPptx(p)).save(candidate);
const norm=spawnSync('/Users/zhangshizhuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python',[path.join(root,'scripts/normalize_chart_export.py'),candidate],{encoding:'utf8'});if(norm.status!==0)throw new Error(norm.stderr);
const skill='/Users/zhangshizhuo/.codex/plugins/cache/openai-primary-runtime/presentations/26.905.11957/skills/presentations';
const finalPath=path.join(root,'deliverables/LSGI3213_Equil_Slides.pptx');
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath,pythonExecutable:'/Users/zhangshizhuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python',integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit','--require-native-table-slide','5','--require-native-table-slide','12'],explicitTotalSlideCount:15,requiredNativeTableOwnerSlides:[5,12],requiredNativeChartOwnerSlides:[3,7,8,9,10,11],fontPolicy:{basis:'design',families:['Arial']},materializeLiteralChartWorkbooks:true,verifyArtifactToolImport:true,receiptPath:path.join(stage,'slides_delivery.validation.json')});
console.log(JSON.stringify(result));
await fs.mkdir(path.join(root,'qa/slides'),{recursive:true});
for(let i=0;i<p.slides.items.length;i++){
 const slide=p.slides.items[i];const img=await p.export({slide,format:'png',scale:1.5});
 await fs.writeFile(path.join(root,'qa/slides',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await img.arrayBuffer()));
}
console.log('Rendered all slides');
