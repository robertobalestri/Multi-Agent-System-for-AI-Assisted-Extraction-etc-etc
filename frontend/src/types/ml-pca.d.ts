declare module 'ml-pca' {
  import { Matrix } from 'ml-matrix';
  
  export class PCA {
    constructor(data: number[][]);
    predict(data: number[][], options?: { nComponents?: number }): Matrix;
  }
} 