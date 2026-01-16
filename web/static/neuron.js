
const canvas = document.getElementById('neuron-canvas');
const ctx = canvas.getContext('2d');

let width, height;
let nodes = [];
let links = [];
let particles = [];

// Configuration
const config = {
    nodeCount: 80, // Number of nodes
    linkDistance: 150, // Max distance to connect nodes
    nodeSpeed: 0.5, // Movement speed of nodes
    particleSpeed: 3, // Speed of electrical impulses
    pulseChance: 0.05 // Chance to spawn a new impulse per frame
};

class Node {
    constructor() {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.vx = (Math.random() - 0.5) * config.nodeSpeed;
        this.vy = (Math.random() - 0.5) * config.nodeSpeed;
        this.radius = Math.random() * 2 + 1;
    }

    update() {
        this.x += this.vx;
        this.y += this.vy;

        // Bounce off edges
        if (this.x < 0 || this.x > width) this.vx *= -1;
        if (this.y < 0 || this.y > height) this.vy *= -1;
    }

    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(100, 181, 246, 0.5)';
        ctx.fill();
    }
}

class Particle {
    constructor(startNode, endNode) {
        this.startNode = startNode;
        this.endNode = endNode;
        this.progress = 0;
        this.alive = true;
        // Constants speed regardless of distance
        const dist = Math.hypot(endNode.x - startNode.x, endNode.y - startNode.y);
        this.speed = config.particleSpeed / dist;
    }

    update() {
        this.progress += this.speed;
        if (this.progress >= 1) {
            this.progress = 1;
            this.alive = false;
        }
    }

    draw() {
        const x = this.startNode.x + (this.endNode.x - this.startNode.x) * this.progress;
        const y = this.startNode.y + (this.endNode.y - this.startNode.y) * this.progress;

        ctx.beginPath();
        ctx.arc(x, y, 2, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff';
        ctx.shadowBlur = 8;
        ctx.shadowColor = '#64b5f6';
        ctx.fill();
        ctx.shadowBlur = 0;
    }
}

function resize() {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;
}

function createNetwork() {
    nodes = [];
    // Adjust node count based on area roughly
    const area = width * height;
    const density = 150 * 150; // One node per 150x150 pixels roughly
    const calculatedNodes = Math.floor(area / density) + 20; 
    const count = Math.min(Math.max(calculatedNodes, 30), 100);

    for (let i = 0; i < count; i++) {
        nodes.push(new Node());
    }
}

function drawNetwork() {
    links = []; 
    // Calculate links and draw lines
    for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
            const dx = nodes[i].x - nodes[j].x;
            const dy = nodes[i].y - nodes[j].y;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist < config.linkDistance) {
                links.push({ start: nodes[i], end: nodes[j] });
                
                ctx.beginPath();
                ctx.moveTo(nodes[i].x, nodes[i].y);
                ctx.lineTo(nodes[j].x, nodes[j].y);
                const opacity = 1 - dist / config.linkDistance;
                ctx.strokeStyle = `rgba(100, 181, 246, ${opacity * 0.15})`;
                ctx.lineWidth = 1;
                ctx.stroke();
            }
        }
    }
}

function animate() {
    ctx.clearRect(0, 0, width, height);

    // Update and draw nodes
    nodes.forEach(node => {
        node.update();
        node.draw();
    });

    drawNetwork();

    // Randomly spawn pulses on existing links
    if (Math.random() < config.pulseChance && links.length > 0) {
        const link = links[Math.floor(Math.random() * links.length)];
        const direction = Math.random() < 0.5;
        const particle = new Particle(
            direction ? link.start : link.end,
            direction ? link.end : link.start
        );
        particles.push(particle);
    }

    // Update and draw particles
    for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        p.update();
        p.draw();
        if (!p.alive) {
            particles.splice(i, 1);
        }
    }

    requestAnimationFrame(animate);
}

function init() {
    resize();
    createNetwork();
    animate();
}

window.addEventListener('resize', () => {
    resize();
    createNetwork(); // Re-create on resize to distribute better
});

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
