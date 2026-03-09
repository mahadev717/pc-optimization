document.addEventListener('DOMContentLoaded', () => {
    // 1. THREE.JS 3D BACKGROUND
    const canvas = document.querySelector('#canvas3d');
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 5;

    // Create a digital grid landscape
    const geometry = new THREE.PlaneGeometry(20, 20, 40, 40);
    const material = new THREE.MeshBasicMaterial({
        color: 0x00f3ff,
        wireframe: true,
        transparent: true,
        opacity: 0.2
    });
    const plane = new THREE.Mesh(geometry, material);
    plane.rotation.x = -Math.PI / 2.5;
    plane.position.y = -2;
    scene.add(plane);

    // Particles
    const partGeom = new THREE.BufferGeometry();
    const partCount = 1000;
    const posArray = new Float32Array(partCount * 3);
    for (let i = 0; i < partCount * 3; i++) {
        posArray[i] = (Math.random() - 0.5) * 15;
    }
    partGeom.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    const partMat = new THREE.PointsMaterial({ size: 0.02, color: 0xff3c3c });
    const particles = new THREE.Points(partGeom, partMat);
    scene.add(particles);

    function animate() {
        requestAnimationFrame(animate);

        // Dynamic landscape movement
        const time = Date.now() * 0.001;
        const positions = plane.geometry.attributes.position.array;
        for (let i = 0; i < positions.length; i += 3) {
            const x = positions[i];
            const y = positions[i + 1];
            positions[i + 2] = Math.sin(x * 0.5 + time) * 0.5 + Math.cos(y * 0.3 + time) * 0.5;
        }
        plane.geometry.attributes.position.needsUpdate = true;

        particles.rotation.y += 0.001;
        particles.rotation.x += 0.0005;

        renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // 2. UI LOGIC
    const loginForm = document.getElementById('login-form');
    const loginModule = document.getElementById('login-module');
    const dashModule = document.getElementById('dash-module');
    const terminal = document.getElementById('terminal-log');
    const memUsage = document.getElementById('mem-usage');

    const CORRECT_USER = '1';
    const CORRECT_PASS = '1';

    // Random memory fluctuation
    setInterval(() => {
        memUsage.innerText = Math.floor(Math.random() * (28 - 22) + 22) + '%';
    }, 2000);

    // Clock
    setInterval(() => {
        document.getElementById('clock').innerText = new Date().toLocaleTimeString();
    }, 1000);

    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const user = document.getElementById('user-input').value;
        const pass = document.getElementById('pass-input').value;

        if (user === CORRECT_USER && pass === CORRECT_PASS) {
            // Success audio feedback (simulated)
            transitionToDashboard();
        } else {
            const error = document.getElementById('login-error');
            error.classList.remove('hidden');
            setTimeout(() => error.classList.add('hidden'), 3000);
        }
    });

    function transitionToDashboard() {
        loginModule.classList.add('fade-out');
        setTimeout(() => {
            loginModule.style.display = 'none';
            dashModule.style.display = 'block';
            dashModule.classList.add('fade-in');

            // Speed up 3D background
            partMat.color.set(0x00f3ff);
            material.opacity = 0.5;
        }, 800);
    }

    // 3. AIM OPTIMIZER LOGIC
    window.runAimOptimizer = async function () {
        try {
            await fetch('/run-optimizer', { method: 'POST' });
        } catch (e) {
            console.error('SERVER_OFFLINE');
        }
    }

    window.restoreDefaults = async function () {
        try {
            await fetch('/restore-defaults', { method: 'POST' });
        } catch (e) {
            console.error('SERVER_OFFLINE');
        }
    }

});
