declare module 'ml-matrix' {
  export class Matrix {
    constructor(rows: number, columns: number);
    static from(array: number[][]): Matrix;
    to2DArray(): number[][];
  }
} 