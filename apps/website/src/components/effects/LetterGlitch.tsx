import { useRef, useEffect } from 'react';

interface LetterGlitchProps {
  glitchColors?: string[];
  glitchSpeed?: number;
  centerVignette?: boolean;
  outerVignette?: boolean;
  smooth?: boolean;
  /**
   * When true (default), at mount the component reads --brand-300, --brand-600,
   * and --brand-900 from :root and uses those as the glitch palette so the
   * effect tracks the active theme. Falls back to `glitchColors` if the
   * tokens can't be resolved.
   */
  useBrandTokens?: boolean;
}

const FALLBACK_COLORS = ['#5e4491', '#A476FF', '#241a38'];
const BRAND_VARS = ['--brand-300', '--brand-600', '--brand-900'];

const LetterGlitch = ({
  glitchColors = FALLBACK_COLORS,
  glitchSpeed = 33,
  centerVignette = false,
  outerVignette = false,
  smooth = true,
  useBrandTokens = true,
}: LetterGlitchProps) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animationRef = useRef<number | null>(null);
  const letters = useRef<
    {
      char: string;
      color: string;
      targetColor: string;
      colorProgress: number;
    }[]
  >([]);
  const grid = useRef({ columns: 0, rows: 0 });
  // Cached canvas dimensions — updated only in resizeCanvas (called on init
  // and on window resize). Reading getBoundingClientRect() per frame from
  // drawLetters() forced a synchronous layout recompute on every animation
  // tick (~215ms total reflow time on the homepage per Lighthouse Insights).
  const dimensions = useRef({ width: 0, height: 0 });
  const context = useRef<CanvasRenderingContext2D | null>(null);
  const lastGlitchTime = useRef(Date.now());
  const activeColors = useRef<string[]>(glitchColors);

  const fontSize = 16;
  const charWidth = 10;
  const charHeight = 20;

  const lettersAndSymbols = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    '!', '@', '#', '$', '&', '*', '(', ')', '-', '_', '+', '=', '/',
    '[', ']', '{', '}', ';', ':', '<', '>', ',',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
  ];

  const getRandomChar = () => {
    return lettersAndSymbols[Math.floor(Math.random() * lettersAndSymbols.length)];
  };

  const getRandomColor = () => {
    const list = activeColors.current;
    return list[Math.floor(Math.random() * list.length)];
  };

  const parseColor = (color: string) => {
    const sixHex = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(color);
    if (sixHex) {
      return {
        r: parseInt(sixHex[1], 16),
        g: parseInt(sixHex[2], 16),
        b: parseInt(sixHex[3], 16),
      };
    }
    const threeHex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i.exec(color);
    if (threeHex) {
      return {
        r: parseInt(threeHex[1] + threeHex[1], 16),
        g: parseInt(threeHex[2] + threeHex[2], 16),
        b: parseInt(threeHex[3] + threeHex[3], 16),
      };
    }
    const rgb = /^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/.exec(color);
    if (rgb) {
      return {
        r: parseInt(rgb[1], 10),
        g: parseInt(rgb[2], 10),
        b: parseInt(rgb[3], 10),
      };
    }
    return null;
  };

  const interpolateColor = (
    start: { r: number; g: number; b: number },
    end: { r: number; g: number; b: number },
    factor: number,
  ) => {
    const result = {
      r: Math.round(start.r + (end.r - start.r) * factor),
      g: Math.round(start.g + (end.g - start.g) * factor),
      b: Math.round(start.b + (end.b - start.b) * factor),
    };
    return `rgb(${result.r}, ${result.g}, ${result.b})`;
  };

  const calculateGrid = (width: number, height: number) => {
    const columns = Math.ceil(width / charWidth);
    const rows = Math.ceil(height / charHeight);
    return { columns, rows };
  };

  const initializeLetters = (columns: number, rows: number) => {
    grid.current = { columns, rows };
    const totalLetters = columns * rows;
    letters.current = Array.from({ length: totalLetters }, () => ({
      char: getRandomChar(),
      color: getRandomColor(),
      targetColor: getRandomColor(),
      colorProgress: 1,
    }));
  };

  const drawLetters = () => {
    if (!context.current || letters.current.length === 0) return;
    const ctx = context.current;
    const { width, height } = dimensions.current;
    ctx.clearRect(0, 0, width, height);
    ctx.font = `${fontSize}px monospace`;
    ctx.textBaseline = 'top';

    letters.current.forEach((letter, index) => {
      const x = (index % grid.current.columns) * charWidth;
      const y = Math.floor(index / grid.current.columns) * charHeight;
      ctx.fillStyle = letter.color;
      ctx.fillText(letter.char, x, y);
    });
  };

  const resizeCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const parent = canvas.parentElement;
    if (!parent) return;

    const dpr = window.devicePixelRatio || 1;
    const rect = parent.getBoundingClientRect();

    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;

    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;

    // Cache so drawLetters can use these on every frame without forcing
    // a fresh layout read.
    dimensions.current = { width: rect.width, height: rect.height };

    if (context.current) {
      context.current.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    const { columns, rows } = calculateGrid(rect.width, rect.height);
    initializeLetters(columns, rows);
    drawLetters();
  };

  const updateLetters = () => {
    if (!letters.current || letters.current.length === 0) return;

    const updateCount = Math.max(1, Math.floor(letters.current.length * 0.05));

    for (let i = 0; i < updateCount; i++) {
      const index = Math.floor(Math.random() * letters.current.length);
      if (!letters.current[index]) continue;

      letters.current[index].char = getRandomChar();
      letters.current[index].targetColor = getRandomColor();

      if (!smooth) {
        letters.current[index].color = letters.current[index].targetColor;
        letters.current[index].colorProgress = 1;
      } else {
        letters.current[index].colorProgress = 0;
      }
    }
  };

  const handleSmoothTransitions = () => {
    let needsRedraw = false;
    letters.current.forEach((letter) => {
      if (letter.colorProgress < 1) {
        letter.colorProgress += 0.05;
        if (letter.colorProgress > 1) letter.colorProgress = 1;

        const startRgb = parseColor(letter.color);
        const endRgb = parseColor(letter.targetColor);
        if (startRgb && endRgb) {
          letter.color = interpolateColor(startRgb, endRgb, letter.colorProgress);
          needsRedraw = true;
        }
      }
    });

    if (needsRedraw) {
      drawLetters();
    }
  };

  const animate = () => {
    const now = Date.now();
    if (now - lastGlitchTime.current >= glitchSpeed) {
      updateLetters();
      drawLetters();
      lastGlitchTime.current = now;
    }

    if (smooth) {
      handleSmoothTransitions();
    }

    animationRef.current = requestAnimationFrame(animate);
  };

  // Resolves brand tokens (e.g. --brand-500: oklch(...)) to plain rgb(r,g,b)
  // strings via a 1×1 canvas. Works for any CSS colour the browser can paint.
  const resolveBrandColors = (): string[] => {
    if (typeof document === 'undefined') return [];
    const tmp = document.createElement('canvas');
    tmp.width = 1;
    tmp.height = 1;
    const tmpCtx = tmp.getContext('2d');
    if (!tmpCtx) return [];
    const root = getComputedStyle(document.documentElement);
    const resolved: string[] = [];
    for (const name of BRAND_VARS) {
      const raw = root.getPropertyValue(name).trim();
      if (!raw) continue;
      tmpCtx.clearRect(0, 0, 1, 1);
      tmpCtx.fillStyle = '#000';
      tmpCtx.fillStyle = raw;
      tmpCtx.fillRect(0, 0, 1, 1);
      const [r, g, b] = tmpCtx.getImageData(0, 0, 1, 1).data;
      resolved.push(`rgb(${r}, ${g}, ${b})`);
    }
    return resolved;
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    context.current = canvas.getContext('2d');

    if (useBrandTokens) {
      const brand = resolveBrandColors();
      if (brand.length > 0) {
        activeColors.current = brand;
      }
    }

    resizeCanvas();

    const prefersReducedMotion =
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (!prefersReducedMotion) {
      animate();
    }

    let resizeTimeout: ReturnType<typeof setTimeout>;

    const handleResize = () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        if (animationRef.current !== null) {
          cancelAnimationFrame(animationRef.current);
        }
        resizeCanvas();
        if (!prefersReducedMotion) {
          animate();
        }
      }, 100);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      if (animationRef.current !== null) {
        cancelAnimationFrame(animationRef.current);
      }
      window.removeEventListener('resize', handleResize);
    };
  }, [glitchSpeed, smooth, useBrandTokens]);

  return (
    <div className="relative w-full h-full bg-[#101010] overflow-hidden">
      <canvas ref={canvasRef} className="block w-full h-full" />
      {outerVignette && (
        <div className="absolute top-0 left-0 w-full h-full pointer-events-none bg-[radial-gradient(circle,_rgba(16,16,16,0)_60%,_rgba(16,16,16,1)_100%)]"></div>
      )}
      {centerVignette && (
        <div className="absolute top-0 left-0 w-full h-full pointer-events-none bg-[radial-gradient(circle,_rgba(0,0,0,0.8)_0%,_rgba(0,0,0,0)_60%)]"></div>
      )}
    </div>
  );
};

export default LetterGlitch;
