import * as THREE from '../node_modules/three';
import { SVGLoader } from '../node_modules/three/examples/jsm/loaders/SVGLoader.js';

// 创建场景
const scene = new THREE.Scene();

// 创建相机
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.z = 5;

// 创建渲染器
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// 创建光源
const light = new THREE.AmbientLight(0x404040); // Ambient light
scene.add(light);

const loader = new SVGLoader();

// 加载 SVG 文件
loader.load('../file/phone.svg', function (data) {
    const paths = data.paths;

    const material = new THREE.MeshBasicMaterial({
        color: 0x000000, // 颜色可以根据需要修改
        side: THREE.DoubleSide,
        depthWrite: false
    });
    console.log(paths);
    // 遍历路径并创建几何体
    paths.forEach(path => {
        const shapes = path.toShapes(true);  // 转换为 2D 形状
        shapes.forEach(shape => {
            const geometry = new THREE.ShapeGeometry(shape);
            const mesh = new THREE.Mesh(geometry, material);
            scene.add(mesh);
        });
    });

    // 渲染场景
    animate();
});

// 动画循环
function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
