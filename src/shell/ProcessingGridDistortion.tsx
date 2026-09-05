import { useEffect, useRef } from "react";

export interface ProcessingGridDistortionProps {
  readonly active: boolean;
}

export function ProcessingGridDistortion({
  active,
}: ProcessingGridDistortionProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const activeRef = useRef(active);

  useEffect(() => {
    activeRef.current = active;
  }, [active]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const container = canvas.parentElement;
    if (!container) return;

    const context = canvas.getContext("2d");
    if (!context) return;

    let frame = 0;
    let raf = 0;
    let width = 1;
    let height = 1;
    let dpr = 1;

    const resize = () => {
      const rect = container.getBoundingClientRect();
      dpr = Math.min(window.devicePixelRatio || 1, 1.75);
      width = Math.max(1, Math.floor(rect.width));
      height = Math.max(1, Math.floor(rect.height));
      canvas.width = Math.max(1, Math.floor(width * dpr));
      canvas.height = Math.max(1, Math.floor(height * dpr));
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      context.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(container);
    resize();

    const draw = () => {
      frame += 1;
      context.clearRect(0, 0, width, height);

      const isActive = activeRef.current;
      const spacing = 38;
      const amplitude = isActive ? 10 : 0.75;
      const time = frame * (isActive ? 0.032 : 0.006);
      const focusX = width * 0.58;
      const focusY = height * 0.38;
      const radius = Math.max(width, height) * 0.44;

      context.lineWidth = 1;
      context.strokeStyle = isActive
        ? "rgba(101, 199, 239, 0.115)"
        : "rgba(101, 199, 239, 0.035)";

      const distort = (x: number, y: number) => {
        const dx = x - focusX;
        const dy = y - focusY;
        const distance = Math.sqrt(dx * dx + dy * dy);
        const falloff = Math.max(0, 1 - distance / radius);
        const wave =
          Math.sin(distance * 0.026 - time * 5.3) *
          Math.sin((x + y) * 0.008 + time) *
          falloff;

        const swirl = Math.sin(time * 1.7 + distance * 0.012) * falloff;
        const nx = distance > 0 ? dx / distance : 0;
        const ny = distance > 0 ? dy / distance : 0;

        return {
          x: x + nx * wave * amplitude + -ny * swirl * amplitude * 0.34,
          y: y + ny * wave * amplitude + nx * swirl * amplitude * 0.34,
        };
      };

      for (let x = -spacing; x <= width + spacing; x += spacing) {
        context.beginPath();
        for (let y = -spacing; y <= height + spacing; y += 8) {
          const point = distort(x, y);
          if (y === -spacing) context.moveTo(point.x, point.y);
          else context.lineTo(point.x, point.y);
        }
        context.stroke();
      }

      for (let y = -spacing; y <= height + spacing; y += spacing) {
        context.beginPath();
        for (let x = -spacing; x <= width + spacing; x += 8) {
          const point = distort(x, y);
          if (x === -spacing) context.moveTo(point.x, point.y);
          else context.lineTo(point.x, point.y);
        }
        context.stroke();
      }

      if (isActive) {
        const gradient = context.createRadialGradient(
          focusX,
          focusY,
          0,
          focusX,
          focusY,
          radius * 0.6,
        );
        gradient.addColorStop(0, "rgba(101, 199, 239, 0.075)");
        gradient.addColorStop(0.45, "rgba(101, 199, 239, 0.022)");
        gradient.addColorStop(1, "rgba(101, 199, 239, 0)");
        context.fillStyle = gradient;
        context.fillRect(0, 0, width, height);
      }

      raf = window.requestAnimationFrame(draw);
    };

    raf = window.requestAnimationFrame(draw);

    return () => {
      window.cancelAnimationFrame(raf);
      resizeObserver.disconnect();
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className={`processing-grid-distortion ${active ? "active" : "idle"}`}
      aria-hidden="true"
    />
  );
}
