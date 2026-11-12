import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root=path.resolve(process.argv[2] ?? 'outputs/stockwise-inventory-analysis');
const previewDir=path.join(root,'.workbook-preview');
await fs.mkdir(previewDir,{recursive:true});
const data=JSON.parse(await fs.readFile(path.join(root,'reports/analysis.json'),'utf8'));
const wb=Workbook.create(),s=wb.worksheets.add('Purchase plan'),source=wb.worksheets.add('Inputs');
for(const sheet of [s,source]){sheet.showGridLines=false;sheet.getRange('A1:M65').format.font={name:'Arial',size:10,color:'#17283C'};sheet.getRange('A1:M65').format.rowHeight=22;sheet.getRange('A1:M65').format.verticalAlignment='center';}
s.tabColor='#102538';source.tabColor='#829BB3';
s.getRange('A2').values=[['StockWise | Purchase plan']];s.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:'#102538'};
s.getRange('A3').values=[['Simulated retailer · CAD · 31 October 2026 · amber cells are editable assumptions']];
s.getRange('A3').format.font={name:'Arial',size:10,italic:true,color:'#65768B'};
for(const [col,label,value] of [['A','Demand factor',1],['D','Lead factor',1],['F','Safety days',4],['H','Review days',7],['K','Budget · CAD',8000]]){
 s.getRange(`${col}5`).values=[[label]];s.getRange(`${col}6`).values=[[value]];s.getRange(`${col}6`).format.fill='#FFF0CD';s.getRange(`${col}6`).format.font={name:'Arial',size:12,bold:true,color:'#744F00'};
}
s.getRange('A6').setNumberFormat('0.0"x"');s.getRange('D6').setNumberFormat('0.0"x"');s.getRange('K6').setNumberFormat('$#,##0.00');
for(const [range,min,max] of [['F6',0,30],['H6',1,30],['K6',0,1000000]])s.dataValidations.add({range,rule:{type:'whole',operator:'between',formula1:min,formula2:max}});
s.getRange('A8').values=[['Planned spend']];s.getRange('B8').formulas=[['=IF(B9="Valid",SUM(L12:L59),"INVALID INPUT")']];
s.getRange('D8').values=[['Unspent budget']];s.getRange('E8').formulas=[['=IF(B9="Valid",K6-B8,"INVALID INPUT")']];
s.getRange('H8').values=[['Funded lines']];s.getRange('I8').formulas=[['=IF(B9="Valid",COUNTIF(K12:K59,">0"),"INVALID INPUT")']];
s.getRange('B8').setNumberFormat('$#,##0.00');s.getRange('E8').setNumberFormat('$#,##0.00');
s.getRange('A9').values=[['Input status']];s.getRange('B9').formulas=[['=IF(AND(A6>=0.1,A6<=3,D6>=0.1,D6<=3,F6>=0,F6<=30,H6>=1,H6<=30,K6>=0,K6<=1000000,COUNT(A6,D6,F6,H6,K6)=5),"Valid","INVALID INPUT")']];
s.getRange('D9').values=[['Fixed baseline cover priority; full catalog only. All open PO units count toward position.']];
s.getRange('D9').format.font={name:'Arial',size:10,italic:true,color:'#65768B'};
const headers=['SKU','Product','Position units','Demand / day','Lead days','Pack units','Cost / unit','Reorder point','Target units','Requested qty','Funded qty','Spend · CAD','Budget left'];
s.getRange('A11:M11').values=[headers];
source.getRange('A2').values=[['Planning inputs | simulated snapshot']];source.getRange('A2').format.font={name:'Arial',size:16,bold:true};
source.getRange('A3').values=[['Source: data/planning_inputs.csv; src/build.py + sql/inventory.sql; synthetic seed 1221.']];
source.getRange('A4').values=[['Demand = sales on positive-closing-stock days / those days. Review bias, inbound timing and shelf life before approval.']];
source.getRange('A6:K6').values=[['SKU','Product','Category','Supplier','On hand','On order','Daily demand','Lead days','Pack size','Unit cost','In-stock days']];
source.getRange('A7:K54').values=data.rows.map(p=>[p.sku,p.product,p.category,p.supplier,p.on_hand,p.on_order,p.daily_demand,p.lead_days,p.pack_size,p.unit_cost,p.in_stock_days]);
for(let i=0;i<48;i++){
 const r=i+12,t=i+7,remaining=i===0?'$K$6':`M${r-1}`;
 const formulas=[`=Inputs!A${t}`,`=Inputs!B${t}`,`=Inputs!E${t}+Inputs!F${t}`,`=Inputs!G${t}*$A$6`,`=Inputs!H${t}*$D$6`,`=Inputs!I${t}`,`=Inputs!J${t}`,`=D${r}*(E${r}+$F$6)`,`=D${r}*(E${r}+$F$6+$H$6)`,`=IF($B$9<>"Valid","INVALID",IF(C${r}<=H${r},ROUNDUP(MAX(0,I${r}-C${r})/F${r},0)*F${r},0))`,`=IF($B$9<>"Valid","INVALID",MIN(J${r},ROUNDDOWN(MAX(0,${remaining})/(G${r}*F${r}),0)*F${r}))`,`=IF($B$9<>"Valid","INVALID",ROUND(K${r}*G${r},2))`,`=IF($B$9<>"Valid","INVALID",ROUND(${remaining}-L${r},2))`];
 s.getRange(`A${r}:M${r}`).formulas=[formulas];
 if(i%2===0){s.getRange(`A${r}:M${r}`).format.fill='#F0F5F9';source.getRange(`A${t}:K${t}`).format.fill='#F0F5F9';}
}
for(const [range,width] of [['A1:A59',13],['B1:B59',24],['C1:C59',15],['D1:M59',15]])s.getRange(range).format.columnWidth=width;
for(const [range,width] of [['A1:A54',13],['B1:B54',23],['C1:C54',19],['D1:D54',26],['E1:K54',15]])source.getRange(range).format.columnWidth=width;
for(const [sheet,range] of [[s,'A11:M11'],[source,'A6:K6']]){sheet.getRange(range).format={fill:'#102538',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',rowHeight:34,wrapText:true};}
s.getRange('C12:M59').format.horizontalAlignment='right';source.getRange('E7:K54').format.horizontalAlignment='right';
s.getRange('C12:M59').setNumberFormat('0');s.getRange('D12:E59').setNumberFormat('0.0');s.getRange('G12:G59').setNumberFormat('$0.00');s.getRange('H12:I59').setNumberFormat('0.0');s.getRange('L12:M59').setNumberFormat('$#,##0.00');source.getRange('G7:G54').setNumberFormat('0.0000');source.getRange('J7:J54').setNumberFormat('$0.00');
s.getRange('K12:K59').conditionalFormats.add('cellIs',{operator:'greaterThan',formula:0,format:{fill:'#E2F3D4',font:{color:'#2D5E1B'}}});
s.getRange('B9').conditionalFormats.add('containsText',{text:'INVALID',format:{fill:'#FCE1E5',font:{color:'#A61E3B',bold:true}}});
s.freezePanes.freezeRows(11);source.freezePanes.freezeRows(6);
wb.recalculate();
let spend=Number(s.getRange('B8').values[0][0]);assert.ok(Math.abs(spend-5717.58)<.01,`Baseline spend ${spend}`);
const base=s.getRange('J12:M59').values;assert.ok(base.every(r=>r.every(v=>typeof v==='number'&&Number.isFinite(v))));
s.getRange('K6').values=[[0]];wb.recalculate();assert.equal(s.getRange('B8').values[0][0],0);
s.getRange('K6').values=[[8000]];s.getRange('A6').values=[[2]];wb.recalculate();assert.ok(s.getRange('B8').values[0][0]>spend);assert.ok(s.getRange('B8').values[0][0]<=8000);
s.getRange('A6').values=[[1]];wb.recalculate();assert.ok(Math.abs(s.getRange('B8').values[0][0]-spend)<.01);
s.getRange('K6').values=[[-1]];wb.recalculate();assert.equal(s.getRange('B8').values[0][0],'INVALID INPUT');
s.getRange('K6').values=[[8000]];wb.recalculate();
console.log((await wb.inspect({kind:'region',sheetId:'Purchase plan',range:'A5:M12',maxChars:1800,tableMaxRows:8,tableMaxCols:13})).ndjson);
for(const sheetName of ['Purchase plan','Inputs']){const img=await wb.render({sheetName,range:sheetName==='Purchase plan'?'A1:M22':'A1:K18',scale:1,format:'png'});await fs.writeFile(path.join(previewDir,sheetName.replaceAll(' ','-')+'.png'),new Uint8Array(await img.arrayBuffer()));}
const out=await SpreadsheetFile.exportXlsx(wb);await out.save(path.join(root,'StockWise-Purchasing-Model.xlsx'));
await fs.writeFile(path.join(previewDir,'verification.json'),JSON.stringify({baselineSpend:spend,formulaRows:48,zeroBudgetPassed:true,demandSensitivityPassed:true,baseline:base},null,2));
console.log('Workbook exported; baseline, budget and sensitivity checks passed.');

