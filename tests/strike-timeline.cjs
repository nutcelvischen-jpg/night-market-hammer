// Run with THREE_TEST_MODULE=/path/to/three.cjs node tests/strike-timeline.cjs
// Executes the production timeline using real Three.js transforms, without a GPU.
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const THREE = { ...require(process.env.THREE_TEST_MODULE || 'three') };
const elements = new Map(), pendingLoads = [];
function el(id) {
  if (!elements.has(id)) elements.set(id, { style: {}, dataset: { speed: '.25' }, children: [],
    classList: { add() {}, remove() {}, toggle() {} }, addEventListener() {},
    setAttribute(k,v) { this[k] = v; }, appendChild(c) { this.children.push(c); } });
  return elements.get(id);
}
THREE.WebGLRenderer = class { constructor(){this.shadowMap={};this.domElement=el('canvas');} setSize(){} setPixelRatio(){} render(){} };
THREE.OrbitControls = class { constructor(){this.target=new THREE.Vector3();} update(){} };
THREE.GLTFLoader = class { load(url,cb){pendingLoads.push(()=>{
  const data = fs.readFileSync(require('path').join(__dirname,'..',url));
  const gltf = JSON.parse(data.subarray(20,20+data.readUInt32LE(12)).toString());
  const nodes = gltf.nodes.map(n => {
    let obj = new THREE.Group();
    if(n.mesh !== undefined) {
      const prim = gltf.meshes[n.mesh].primitives[0];
      const accessor = gltf.accessors[prim.attributes.POSITION];
      const view = gltf.bufferViews[accessor.bufferView];
      const binStart = 20 + data.readUInt32LE(12) + 8;
      const start = binStart + (view.byteOffset || 0) + (accessor.byteOffset || 0);
      const positions = new Float32Array(accessor.count*3);
      for(let i=0;i<accessor.count;i++) for(let c=0;c<3;c++) positions[i*3+c] = data.readFloatLE(start+i*(view.byteStride||12)+c*4);
      const geometry = new THREE.BufferGeometry(); geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));
      obj = new THREE.Mesh(geometry,new THREE.MeshStandardMaterial());
    }
    obj.name = n.name;
    if(n.translation) obj.position.fromArray(n.translation);
    if(n.rotation) obj.quaternion.fromArray(n.rotation);
    if(n.scale) obj.scale.fromArray(n.scale);
    return obj;
  });
  gltf.nodes.forEach((n,i) => (n.children || []).forEach(c => nodes[i].add(nodes[c])));
  const scene = new THREE.Group(); gltf.scenes[gltf.scene || 0].nodes.forEach(i => scene.add(nodes[i]));
  cb({scene});
});} };
let clockNow = 0;
const context = { THREE, console, Math, performance:{now:()=>clockNow}, innerWidth:1280,innerHeight:800,
  requestAnimationFrame(){}, setTimeout(){}, clearTimeout(){}, document:{hidden:false,body:el('body'),
  getElementById:el,createElement:(tag)=>el(`${tag}-${Math.random()}`),createElementNS:(_,tag)=>el(`${tag}-${Math.random()}`),
  querySelector:el,querySelectorAll:()=>[],addEventListener(){}},
  window:{innerWidth:1280,innerHeight:800,devicePixelRatio:1,addEventListener(){},matchMedia:()=>({matches:false})} };
vm.createContext(context);
const html = fs.readFileSync(require('path').join(__dirname,'../index.html'),'utf8');
vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],context);
pendingLoads.forEach(f=>f());
vm.runInContext(`for (const key of Object.getOwnPropertyNames(SoundFX.prototype)) if(key !== 'constructor') sfx[key] = () => {};`, context);
vm.runInContext(`for (const key of Object.getOwnPropertyNames(BossVoice.prototype)) if(key !== 'constructor') boss[key] = () => {}; const voiceEvents = []; boss.play = event => voiceEvents.push(event);`, context);
const run = source => vm.runInContext(source,context);
// Verify the selected asset actually contains no hand/arm meshes.
const assetName = run("assetList.find(a => a.key === 'hammer').url");
const asset = fs.readFileSync(require('path').join(__dirname, '..', assetName));
const gltf = JSON.parse(asset.subarray(20,20+asset.readUInt32LE(12)).toString());
assert(gltf.nodes.filter(n => n.mesh !== undefined).every(n => n.name.startsWith('Hammer_')));
let cases=0;
for (const head of ['flat','sharp']) for(const speed of [.25,.5,1]) for(const power of [0,.4,.75,1]) for(const fps of [10,60,144]) {
  run(`resetNail(); setHeadMode('${head}'); GAME.slowMoSpeed=${speed}; AIM.locked = true; AIM.lockedX = 0; AIM.lockedZ = 0; executeHammerStrike(${power});`);
  let previous=.07, separated=0;
  for(let i=0;i<1600;i++) {
    const result=run(`updateStrike(${1/fps}); (()=>{
      const point=new THREE.Vector3(${head==='flat'?.0675:-.0975},${head==='flat'?.015:.012},0);
      scene.updateMatrixWorld(true); hammerObj.getObjectByName('${head==='flat'?'Hammer_FlatHead':'Hammer_SharpHead'}').localToWorld(point);
      return {height:nails[0].height, active:GAME.isStriking, phase:GAME.phase,
        error:point.distanceTo(new THREE.Vector3(.05,GAME.nailBaseY+GAME.currentProtrusion,0)),
        gap:point.y-(GAME.nailBaseY+GAME.currentProtrusion), counter:sinkNumber.textContent, hud:hudRemainMm.textContent}; })()`);
    assert(result.height <= previous+1e-12,'nail must never rise during drive'); previous=result.height;
    if(result.active) assert.equal(result.counter, ((.07-result.height)*1000).toFixed(1), 'side counter follows actual depth');
    if(result.phase === '命中') assert(result.error<1e-8,`contact drift ${result.error}`);
    if(['回彈 · 釘入','釘身彎折'].includes(result.phase)) { assert(result.gap>0,'hammer must leave the sinking nail'); separated++; }
    if(!result.active)break;
    assert(i<1599,'timeline must terminate');
  }
  const drive=Math.pow(power,1.8)*(head==='sharp'?.092:.072);
  const expected=drive>.0678 || (head==='sharp' && power>.86) ? .042 : Math.max(.0005,.07-drive);
  assert(Math.abs(previous-expected)<1e-10,'final penetration');
  assert(separated>0,'must rebound before penetration ends'); cases++;
}
// The macro camera follows the descending nail after its second push-in.
run(`resetNail(); setHeadMode('flat'); GAME.slowMoSpeed=.25; executeHammerStrike(.75); updateStrike(activeStrike.launch + activeStrike.approach + activeStrike.freeze + .4);`);
const trackedY = run('controls.target.y');
run('updateStrike(.2)');
assert(run('controls.target.y') < trackedY, 'closeup follows the nail downward');
for(let i=0;i<240;i++) run('updateStrike(1/60)');
// At the same real time after release the hammer must move up while the nail moves down.
run(`resetNail(); setHeadMode('flat'); executeHammerStrike(.75); updateStrike(activeStrike.launch + activeStrike.approach + activeStrike.freeze);`);
assert(run('Math.abs(faceWorld.y - (GAME.nailBaseY + GAME.currentProtrusion))') < 1e-10);
run('updateStrike(activeStrike.contact + .01)');
const released = run('({hammer:faceWorld.y,nail:GAME.currentProtrusion})');
run('updateStrike(.03)');
assert(run('faceWorld.y') > released.hammer, 'hammer rises immediately after contact');
assert(run('GAME.currentProtrusion') < released.nail, 'nail continues sinking independently');
for(let i=0;i<240;i++) run('updateStrike(1/60)');
run(`resetNail(); setHeadMode('flat'); reducedMotion.matches = true; const before=camera.position.clone(); executeHammerStrike(.7);`);
for(let i=0;i<180;i++) run('updateStrike(1/60)');
assert(run('camera.position.distanceTo(before)')<1e-10,'reduced motion keeps camera still');
run(`resetNail(); setHeadMode('flat'); GAME.slowMoSpeed=.25; executeHammerStrike(.5);`);
for(let i=0;i<240;i++)run('updateStrike(1/60)');
const first=run('GAME.currentProtrusion');
run('executeHammerStrike(.5)');for(let i=0;i<240;i++)run('updateStrike(1/60)');
assert(run('GAME.currentProtrusion')<first,'repeat strike must continue from previous height');
run('resetNail()');assert.equal(run('GAME.currentProtrusion'),.07);assert.equal(run('GAME.swingsCount'),0);
// Multi-nail progression, independent geometry, scoring, deadline and restart.
assert.equal(run('nails.length'),5);
const hit = power => { run(`executeHammerStrike(${power})`); for(let i=0;i<300;i++)run('updateStrike(1/60)'); };
run("resetNail(); setHeadMode('flat'); selectNail(3)");
assert.equal(run('GAME.activeNail'),3);
run('executeHammerStrike(.5); selectNail(2)');
assert.equal(run('GAME.activeNail'),3,'selection locked during swing');
run('updateStrike(activeStrike.launch+activeStrike.approach+activeStrike.freeze)');
assert(run(`(()=>{scene.updateMatrixWorld(true); const p=new THREE.Vector3(.0675,.015,0); hammerObj.getObjectByName('Hammer_FlatHead').localToWorld(p); return p.distanceTo(new THREE.Vector3(nails[3].x,GAME.nailBaseY+GAME.currentProtrusion,nails[3].z))<1e-8;})()`),'offset nail contact');
for(let i=0;i<300;i++)run('updateStrike(1/60)');
assert.equal(run('nails[0].height'),.07,'unselected nails unchanged');
run("resetNail(); setHeadMode('flat')");
const perfectPower=Math.pow(.067/.072,1/1.8);
for(let i=0;i<5;i++)hit(perfectPower);
assert.equal(run('RACE.score'),500);assert.equal(run('RACE.completed'),5);assert.equal(run('RACE.phase'),'finished');
const swings=run('GAME.swingsCount');hit(.5);assert.equal(run('GAME.swingsCount'),swings,'finished race blocks input');
run('resetNail()');hit(1);
assert.equal(run('nails[0].state'),'bent');assert.equal(run('RACE.broken'),1);assert.equal(run('RACE.score'),0);assert.equal(run('GAME.activeNail'),1);
assert(run('nails[0].parts[0].mesh.geometry !== nails[1].parts[0].mesh.geometry'),'independent geometry');
assert(run('nails[0].parts.some(p=>p.original.some((v,i)=>Math.abs(v-p.mesh.geometry.attributes.position.array[i])>1e-6))'),'visible bend deforms geometry');
assert(run('nails[1].parts.every(p=>p.original.every((v,i)=>v===p.mesh.geometry.attributes.position.array[i]))'),'other geometry unchanged');
run('selectNail(0)');assert.equal(run('GAME.activeNail'),1,'broken nail unavailable');
run('resetNail()');clockNow=100;run('startCharging()');clockNow=25100;run('updateRaceClock(performance.now())');
assert.equal(run('RACE.phase'),'finished');assert.equal(run('GAME.isCharging'),false,'deadline cancels charge');
run('resetNail()');clockNow=100000;run('startRace()');clockNow=124900;run(`executeHammerStrike(${perfectPower})`);
clockNow=125001;run('updateRaceClock(performance.now())');for(let i=0;i<300;i++)run('updateStrike(1/60)');
assert.equal(run('RACE.score'),0,'late impact cannot score');assert.equal(run('nails[0].height'),.07);
run('resetNail()');clockNow=200000;run(`executeHammerStrike(${perfectPower}); updateStrike(.6)`);
clockNow=225001;run('updateRaceClock(performance.now())');for(let i=0;i<300;i++)run('updateStrike(1/60)');
assert.equal(run('RACE.score'),100,'impact before deadline is credited');assert.equal(run('RACE.phase'),'finished');
run('resetNail()');assert.equal(run('RACE.score'),0);assert.equal(run('RACE.remaining'),25);assert(run("nails.every(n=>n.state==='ready' && n.height===.07 && n.bend===0)"));
// Sharp mode requires an explicit aim lock before charging or striking.
run("resetNail(); setHeadMode('sharp'); executeHammerStrike(.5)");
assert.equal(run('GAME.swingsCount'),0,'cannot bypass aim stage');
run('startCharging()');assert.equal(run('GAME.isCharging'),false);
run('handleStrikePress(); releaseAndStrike()');
assert.equal(run('AIM.locked'),true);assert.equal(run('GAME.isCharging'),false);assert.equal(run('GAME.swingsCount'),0,'first release only locks aim');
const lockedX=run('AIM.lockedX');run('updateAim(performance.now()+10000)');assert.equal(run('AIM.lockedX'),lockedX,'locked aim cannot drift');
run('handleStrikePress()');assert.equal(run('GAME.isCharging'),true,'second press charges');
run('cancelCharge(); selectNail(2)');assert.equal(run('AIM.locked'),false,'new nail requires new aim');
run("AIM.locked=true; setHeadMode('flat'); setHeadMode('sharp')");assert.equal(run('AIM.locked'),false,'head switching invalidates aim');
const sharpHit=(x,z,power)=>{
  run(`resetNail(); setHeadMode('sharp'); AIM.locked=true; AIM.lockedX=${x}; AIM.lockedZ=${z}; executeHammerStrike(${power});`);
  for(let i=0;i<300;i++) run('updateStrike(1/60)');
};
sharpHit(0,0,.5);const centerHeight=run('nails[0].height');
assert(centerHeight<.07);assert.equal(run('AIM.locked'),false,'every swing requires fresh aim');
sharpHit(.004,0,.5);assert(run('nails[0].height')>centerHeight,'off-center loses penetration');
sharpHit(.009,0,.7);assert.equal(run('nails[0].state'),'bent','edge heavy hit bends nail');
sharpHit(.014,.005,1);assert.equal(run('nails[0].height'),.07,'miss does not move nail');assert.equal(run('RACE.score'),0);assert.equal(run('RACE.broken'),0);assert.equal(run('GAME.swingsCount'),1,'miss costs a swing');
run("resetNail(); setHeadMode('sharp'); AIM.locked=true; AIM.lockedX=.006; AIM.lockedZ=.004; executeHammerStrike(.4); updateStrike(activeStrike.launch+activeStrike.approach+activeStrike.freeze)");
assert(run(`(()=>{scene.updateMatrixWorld(true); const p=new THREE.Vector3(-.0975,.012,0); hammerObj.getObjectByName('Hammer_SharpHead').localToWorld(p); return Math.abs(p.x-(GAME.nailX+.006))<1e-8 && Math.abs(p.z-(GAME.nailZ+.004))<1e-8;})()`),'sharp contact follows locked aim in world coordinates');
for(let i=0;i<300;i++)run('updateStrike(1/60)');
run("resetNail(); setHeadMode('sharp'); handleStrikePress()");clockNow+=25001;run('updateRaceClock(performance.now()); handleStrikePress()');
assert.equal(run('RACE.phase'),'finished');assert.equal(run('AIM.locked'),false);assert.equal(run('GAME.isCharging'),false,'deadline blocks power stage');
run("resetNail(); setHeadMode('flat'); handleStrikePress()");assert.equal(run('GAME.isCharging'),true,'flat head still charges immediately');run('cancelCharge()');
console.log(`PASS: ${cases} timeline/rebound cases, synchronized counter, descending camera, hammer-only asset, reduced motion, consecutive strikes, five-nail scoring, deformation isolation, deadline boundaries, restart, sharp aim gating, accuracy, miss and edge-hit outcomes.`);

// Voice events follow authoritative outcomes, never charge strength alone.
run("resetNail(); voiceEvents.length=0; setHeadMode('flat')"); hit(perfectPower);
assert.equal(run("voiceEvents.join(',')"),'intro,success');
run("resetNail(); voiceEvents.length=0"); hit(1);
assert.equal(run("voiceEvents.join(',')"),'intro,bent');
run("voiceEvents.length=0"); sharpHit(.014,.005,1);
assert.equal(run("voiceEvents.join(',')"),'intro,miss');
run("resetNail(); voiceEvents.length=0; setHeadMode('flat')"); hit(.4); hit(.4);
assert.equal(run("voiceEvents.join(',')"),'intro','partial hits stay quiet; intro only once per race');
run("resetNail(); voiceEvents.length=0; executeHammerStrike(.96)"); clockNow+=25001;
for(let i=0;i<300;i++)run('updateStrike(1/60)');
assert.equal(run("voiceEvents.join(',')"),'intro','late impact cannot earn success voice');
console.log('PASS: intro once, success/bent/miss routing, partial-hit silence, late-hit silence.');

// Hard mode uses honest power markers, faster pacing and deterministic penalties.
run("resetNail(); setHeadMode('flat')"); assert.equal(run('RACE.duration'),25); hit(1); assert.equal(run('RACE.remaining'),18);
sharpHit(.014,.005,1); assert.equal(run('RACE.remaining'),21);
assert.equal(run('aimQuality(.006,0).edge'),true);assert.equal(run('aimQuality(.0025,0).label'),'偏心 · 穿透減弱');
for (const head of ['flat','sharp']) for (const height of [.07,.03,.01]) {
 run(`resetNail(); setHeadMode('${head}'); GAME.currentProtrusion=${height}; nails[0].height=${height}; AIM.locked=true; AIM.lockedX=0; AIM.lockedZ=0; updateUI();`);
 const low=Number(el('sweet-marker').style.left.replace('%',''))/100, width=Number(el('sweet-marker').style.width.replace('%',''))/100;
 if(width>0){hit(low+width/2);assert.equal(run('nails[0].state'),'done','displayed green interval must succeed');}
}
console.log('PASS: 25-second inferno mode, miss/bend time penalties and accurate narrowed green zones.');

// Guidance must remain honest when an off-center hit cannot finish in one strike.
for(const head of ['flat','sharp']) for(const height of [.07,.03,.01,.004]) for(const x of [0,.002,.004,.005,.008,.012]) {
 run(`resetNail(); setHeadMode('${head}'); GAME.currentProtrusion=${height}; nails[0].height=${height}; AIM.locked=true; AIM.lockedX=${x}; AIM.lockedZ=0; updateUI();`);
 const guide=run('powerGuide()');
 assert.equal(el('sweet-marker').hidden,guide.kind==='miss');
 assert.equal(el('sweet-marker').dataset.guide,guide.kind);
 if(guide.kind==='miss'){assert(el('power-instruction').textContent.includes('無命中區'));continue;}
 assert(guide.high>guide.low && guide.low>=0 && guide.high<=1);
 const startingHeight=run('GAME.currentProtrusion');hit((guide.low+guide.high)/2);
 assert.equal(run('nails[0].state'),guide.kind==='done'?'done':'ready');
 assert(run('nails[0].height')<startingHeight);
 if(guide.kind==='partial')assert(el('sweet-marker').style.width!=='0%');
}
run("resetNail(); setHeadMode('sharp'); AIM.locked=true; AIM.lockedX=.014; AIM.lockedZ=0; updateUI()");
assert.equal(el('sweet-marker').hidden,true);
run('AIM.lockedX=0;updateUI()');assert.equal(el('sweet-marker').hidden,false);
console.log('PASS: green/amber/miss guidance, partial-hit safety, and restoration after reaim.');
