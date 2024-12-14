interface WebGLExtension {
  [key: string]: any;
}

interface WebGLRenderingContext extends RenderingContext {
  getExtension(name: string): WebGLExtension | null;
} 