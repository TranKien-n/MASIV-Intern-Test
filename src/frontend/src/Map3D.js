import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";

// Choose a base color by building type / zoning
function baseColorForBuilding(b) {
  const type = (b.type || "").toLowerCase();
  const zoning = (b.zoning || "").toUpperCase();

  if (type === "commercial" || zoning.startsWith("C-")) {
    return 0x4a90e2; // blue
  }
  if (type === "residential" || zoning.startsWith("RC")) {
    return 0xf5deb3; // beige
  }
  return 0xb0c4de; // grey-blue
}

export default function Map3D({
  buildings,
  filteredIds,
  selectedBuilding,
  onSelectBuilding,
}) {
  const mountRef = useRef(null);
  const meshesRef = useRef([]);
  const cameraRef = useRef(null);
  const controlsRef = useRef(null);

  const targetCenterRef = useRef(new THREE.Vector3());
  const cameraPosTargetRef = useRef(new THREE.Vector3());
  const baseCenterRef = useRef(new THREE.Vector3());
  const baseSpanRef = useRef(100);

  const animatingRef = useRef(false); // 🔹 are we currently auto-animating?

  const [hoverInfo, setHoverInfo] = useState(null);

  // --- Initial scene setup & rendering ---
  useEffect(() => {
    if (!mountRef.current || buildings.length === 0) return;

    const container = mountRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Compute base bounding box & average height (all buildings)
    let minX = Infinity,
      maxX = -Infinity;
    let minY = Infinity,
      maxY = -Infinity;
    let sumH = 0;
    let countH = 0;

    buildings.forEach((b) => {
      const h = b.height || 10;
      sumH += h;
      countH += 1;

      (b.footprint || []).forEach(([x, y]) => {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      });
    });

    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;
    const span = Math.max(maxX - minX, maxY - minY) || 100;
    const avgH = countH > 0 ? sumH / countH : 10;

    baseCenterRef.current.set(centerX, centerY, 0);
    baseSpanRef.current = span;

    const TARGET_AVG_VISUAL = span * 0.18;
    const HEIGHT_SCALE = avgH > 0 ? TARGET_AVG_VISUAL / avgH : 0.5;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf5f5f5);

    // Camera
    const camera = new THREE.PerspectiveCamera(50, width / height, 1, 10000);
    const initialPos = new THREE.Vector3(
      centerX + span * 0.9,
      centerY - span * 0.9,
      span * 1.5
    );
    camera.position.copy(initialPos);
    camera.up.set(0, 0, 1);
    camera.lookAt(centerX, centerY, 0);

    cameraRef.current = camera;
    targetCenterRef.current.set(centerX, centerY, 0);
    cameraPosTargetRef.current.copy(initialPos);
    animatingRef.current = false; // start with no auto animation

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio || 1);
    renderer.setSize(width, height);
    container.appendChild(renderer.domElement);

    // Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.screenSpacePanning = false;
    controls.minDistance = span * 0.3;
    controls.maxDistance = span * 4.0;
    controls.maxPolarAngle = Math.PI / 2.05;
    controlsRef.current = controls;

    // 🔹 If user starts interacting, stop auto animation
    const cancelAnimation = () => {
      animatingRef.current = false;
    };
    controls.addEventListener("start", cancelAnimation);

    // Lights
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.9);
    dirLight.position.set(centerX + span, centerY + span, span * 3);
    scene.add(dirLight);

    const ambient = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambient);

    // Grid only (no plane/wall)
    const groundSize = span * 2;
    const gridDivisions = 20;
    const grid = new THREE.GridHelper(
      groundSize,
      gridDivisions,
      0xcccccc,
      0xdddddd
    );
    grid.rotation.x = Math.PI / 2;
    grid.position.set(centerX, centerY, 0.01);
    scene.add(grid);

    const meshes = [];
    meshesRef.current = meshes;

    // Buildings
    buildings.forEach((b) => {
      const coords = b.footprint;
      if (!coords || coords.length < 3) return;

      const shape = new THREE.Shape();
      coords.forEach(([x, y], idx) => {
        if (idx === 0) shape.moveTo(x, y);
        else shape.lineTo(x, y);
      });

      const realH = b.height || 10;
      const visualHeight = realH * HEIGHT_SCALE;

      const geom = new THREE.ExtrudeGeometry(shape, {
        depth: visualHeight,
        bevelEnabled: false,
      });

      const baseColor = new THREE.Color(baseColorForBuilding(b));
      const mat = new THREE.MeshStandardMaterial({
        color: baseColor,
        roughness: 0.6,
        metalness: 0.0,
      });

      const mesh = new THREE.Mesh(geom, mat);
      mesh.userData = { id: b.id, data: b, baseColor };

      scene.add(mesh);

      const edgeGeom = new THREE.EdgesGeometry(geom);
      const edgeMat = new THREE.LineBasicMaterial({ color: 0x444444 });
      const edges = new THREE.LineSegments(edgeGeom, edgeMat);
      edges.position.copy(mesh.position);
      scene.add(edges);

      meshes.push(mesh);
    });

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    function handleClick(event) {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const hits = raycaster.intersectObjects(meshes);
      if (hits.length > 0) {
        const mesh = hits[0].object;
        onSelectBuilding(mesh.userData.data);
      }
    }

    function handleMouseMove(event) {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const hits = raycaster.intersectObjects(meshes);

      if (hits.length > 0) {
        const mesh = hits[0].object;
        const b = mesh.userData.data;
        setHoverInfo({
          id: b.id,
          name: b.name,
          height: b.height,
          x: event.clientX - rect.left,
          y: event.clientY - rect.top,
        });
      } else {
        setHoverInfo(null);
      }
    }

    function handleMouseLeave() {
      setHoverInfo(null);
    }

    renderer.domElement.addEventListener("click", handleClick);
    renderer.domElement.addEventListener("mousemove", handleMouseMove);
    renderer.domElement.addEventListener("mouseleave", handleMouseLeave);

    function handleResize() {
      if (!mountRef.current) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    }

    window.addEventListener("resize", handleResize);

    function animate() {
      requestAnimationFrame(animate);

      if (cameraRef.current && controlsRef.current) {
        if (animatingRef.current) {
          // Smoothly interpolate camera & target toward their targets
          cameraRef.current.position.lerp(cameraPosTargetRef.current, 0.1);
          controlsRef.current.target.lerp(targetCenterRef.current, 0.1);
          controlsRef.current.update();

          const camDist = cameraRef.current.position.distanceTo(
            cameraPosTargetRef.current
          );
          const tgtDist = controlsRef.current.target.distanceTo(
            targetCenterRef.current
          );

          // Stop animating when we're very close
          if (camDist < 0.5 && tgtDist < 0.5) {
            animatingRef.current = false;
          }
        } else {
          // Normal user-controlled orbiting
          controlsRef.current.update();
        }
      }

      renderer.render(scene, camera);
    }
    animate();

    return () => {
      window.removeEventListener("resize", handleResize);
      renderer.domElement.removeEventListener("click", handleClick);
      renderer.domElement.removeEventListener("mousemove", handleMouseMove);
      renderer.domElement.removeEventListener("mouseleave", handleMouseLeave);
      controls.removeEventListener("start", cancelAnimation);
      container.removeChild(renderer.domElement);
      controls.dispose();
      renderer.dispose();
      meshesRef.current = [];
    };
  }, [buildings, onSelectBuilding]);

  // --- Highlight filtered buildings ---
  useEffect(() => {
    const meshes = meshesRef.current || [];
    meshes.forEach((m) => {
      const id = m.userData.id;
      if (filteredIds && filteredIds.includes(id)) {
        m.material.color.set(0xff4444); // highlight
      } else if (m.userData.baseColor) {
        m.material.color.copy(m.userData.baseColor);
      }
    });
  }, [filteredIds]);

  // --- Smooth camera re-targeting on selection / filter ---
  useEffect(() => {
    if (!cameraRef.current || buildings.length === 0) return;

      let focusBuildings = null;

    if (selectedBuilding) {
      // Always ease to clicked building
      focusBuildings = [selectedBuilding];
    } else if (filteredIds && filteredIds.length === 1) {
      // Ease only when exactly one building matches the query
      focusBuildings = buildings.filter((b) => b.id === filteredIds[0]);
    } else if (filteredIds && filteredIds.length > 1) {
      // Multiple results: do not move camera
      animatingRef.current = false;
      return;
    }
    // No focus set: go back to base center
    if (!focusBuildings || focusBuildings.length === 0) {
      const center = baseCenterRef.current;
      const span = baseSpanRef.current;
      targetCenterRef.current.set(center.x, center.y, 0);
      cameraPosTargetRef.current.set(
        center.x + span * 0.9,
        center.y - span * 0.9,
        span * 1.5
      );
      animatingRef.current = true; // smooth reset
      return;
    }

    // Compute bounding box of focused subset
    let minX = Infinity,
      maxX = -Infinity;
    let minY = Infinity,
      maxY = -Infinity;

    focusBuildings.forEach((b) => {
      (b.footprint || []).forEach(([x, y]) => {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      });
    });

    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;
    const span = Math.max(maxX - minX, maxY - minY) || baseSpanRef.current;

    targetCenterRef.current.set(centerX, centerY, 0);

    const distFactor = 1.3;
    cameraPosTargetRef.current.set(
      centerX + span * distFactor,
      centerY - span * distFactor,
      span * 1.6
    );

    // 🔹 Trigger a new smooth animation towards this focus
    animatingRef.current = true;
  }, [filteredIds, selectedBuilding, buildings]);

  return (
    <div
      ref={mountRef}
      style={{
        position: "relative",
        width: "100%",
        height: "600px",
        border: "1px solid #ccc",
      }}
    >
      {hoverInfo && (
        <div
          style={{
            position: "absolute",
            left: hoverInfo.x + 10,
            top: hoverInfo.y + 10,
            background: "rgba(0,0,0,0.75)",
            color: "#fff",
            padding: "4px 8px",
            borderRadius: 4,
            fontSize: 12,
            pointerEvents: "none",
            maxWidth: 200,
          }}
        >
          <div>
            <b>{hoverInfo.name || hoverInfo.id}</b>
          </div>
          <div>Height: {hoverInfo.height} m</div>
        </div>
      )}
    </div>
  );
}
