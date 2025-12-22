const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
let W, H;
function resize(){
  const ratio = Math.min(window.innerWidth/800, window.innerHeight/600);
  W = Math.floor(800*ratio);
  H = Math.floor(600*ratio);
  canvas.width = W; canvas.height = H;
}
window.addEventListener('resize', resize); resize();

// Input
const keys = {};
window.addEventListener('keydown', e=> keys[e.code]=true);
window.addEventListener('keyup', e=> keys[e.code]=false);

// Entities
const player = {x: W/2, y: H-60, w: 36, h: 20, speed: 320, cooldown:0};
let bullets = [];
let enemies = [];
let lastTime = 0;
let spawnTimer = 0; 
let score = 0;
let alive = true;

function spawnEnemy(){
  const w = 28, h = 18;
  const x = Math.random()*(W-2*w)+w;
  const speed = 60 + Math.random()*120 + score*0.2;
  enemies.push({x,y: -h, w, h, speed});
}

function update(dt){
  if(!alive) return;
  // move player
  if(keys['ArrowLeft']||keys['KeyA']) player.x -= player.speed*dt;
  if(keys['ArrowRight']||keys['KeyD']) player.x += player.speed*dt;
  player.x = Math.max(player.w/2, Math.min(W-player.w/2, player.x));

  // shooting
  player.cooldown -= dt;
  if((keys['Space'] || keys['KeyK']) && player.cooldown<=0){
    bullets.push({x:player.x, y:player.y-12, r:5, speed:480});
    player.cooldown = 0.18;
  }

  // bullets
  bullets.forEach(b=> b.y -= b.speed*dt);
  bullets = bullets.filter(b=> b.y+ b.r > -10);

  // enemies
  spawnTimer += dt;
  if(spawnTimer> Math.max(0.45, 1.2 - score*0.01)){
    spawnTimer = 0; spawnEnemy();
  }
  enemies.forEach(e=> e.y += e.speed*dt);

  // collisions
  for(let i=enemies.length-1;i>=0;i--){
    const e=enemies[i];
    // enemy hits player
    if(e.y + e.h/2 >= player.y - player.h/2){
      if(Math.abs(e.x-player.x) < (e.w+player.w)/2){ alive=false; }
    }
    // bullet hits enemy
    for(let j=bullets.length-1;j>=0;j--){
      const b=bullets[j];
      if(b.x > e.x - e.w/2 && b.x < e.x + e.w/2 && b.y > e.y - e.h/2 && b.y < e.y + e.h/2){
        enemies.splice(i,1); bullets.splice(j,1); score += 10; break;
      }
    }
  }
  // remove offscreen enemies
  enemies = enemies.filter(e=> e.y - e.h < H+50);
}

function draw(){
  // clear
  ctx.fillStyle = '#071022'; ctx.fillRect(0,0,W,H);

  // player
  ctx.save(); ctx.translate(player.x, player.y);
  ctx.fillStyle = '#6cf'; ctx.fillRect(-player.w/2, -player.h/2, player.w, player.h);
  // gun
  ctx.fillStyle = '#e6f'; ctx.fillRect(-4, -player.h/2 - 8, 8, 8);
  ctx.restore();

  // bullets
  ctx.fillStyle = '#ffd'; bullets.forEach(b=> ctx.beginPath(), ctx.arc(b.x,b.y,b.r,0,Math.PI*2), ctx.fill());

  // enemies
  enemies.forEach(e=>{
    ctx.save(); ctx.translate(e.x,e.y);
    ctx.fillStyle = '#f66'; ctx.fillRect(-e.w/2, -e.h/2, e.w, e.h);
    ctx.restore();
  });

  // UI
  document.getElementById('score').textContent = `Score: ${score}`;
  if(!alive){
    ctx.fillStyle='rgba(0,0,0,0.6)'; ctx.fillRect(0,0,W,H);
    ctx.fillStyle='#fff'; ctx.font = '28px sans-serif'; ctx.textAlign='center';
    ctx.fillText('You died — press R to restart', W/2, H/2);
  }
}

function loop(ts){
  if(!lastTime) lastTime = ts; const dt = Math.min(0.05,(ts-lastTime)/1000); lastTime = ts;
  update(dt); draw(); requestAnimationFrame(loop);
}

window.addEventListener('keydown', e=>{
  if(!alive && e.code === 'KeyR'){ restart(); }
});

function restart(){
  bullets=[]; enemies=[]; score=0; alive=true; player.x = W/2; spawnTimer=0; player.cooldown=0;
}

requestAnimationFrame(loop);