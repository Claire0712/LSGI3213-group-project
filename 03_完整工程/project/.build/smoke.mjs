import fs from 'node:fs/promises';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const p=Presentation.create({slideSize:{width:1280,height:720}});const s=p.slides.add();
const t=s.shapes.add({geometry:'textbox',position:{left:64,top:48,width:1100,height:80},fill:'none',line:{fill:'none',width:0}});t.text='MATSim scenario comparison';t.text.style={typeface:'Arial',fontSize:42,color:'#18354A'};
s.charts.add('bar',{position:{left:90,top:160,width:1000,height:400},categories:['Baseline','Capacity'],series:[{name:'Minutes',values:[22,19],fill:'#3C5488'}],hasLegend:false,xAxis:{textStyle:{typeface:'Arial',fontSize:22}},yAxis:{textStyle:{typeface:'Arial',fontSize:20},title:'Travel time (min)'},dataLabels:{showValue:true,position:'outEnd',textStyle:{typeface:'Arial',fontSize:20}}});
await (await PresentationFile.exportPptx(p)).save('project/.build/smoke.pptx');
const png=await p.export({slide:s,format:'png',scale:1});await fs.writeFile('project/.build/smoke.png',new Uint8Array(await png.arrayBuffer()));
console.log('ok');
