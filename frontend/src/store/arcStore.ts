import { create } from 'zustand';
import type { NarrativeArc } from '@/architecture/types';

interface ArcState {
  arcs: NarrativeArc[];
  selectedArc: NarrativeArc | null;
  isLoading: boolean;
  error: string | null;
  setArcs: (arcs: NarrativeArc[]) => void;
  addArc: (arc: NarrativeArc) => void;
  updateArc: (arc: NarrativeArc) => void;
  deleteArc: (arcId: string) => void;
  setSelectedArc: (arc: NarrativeArc | null) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useArcStore = create<ArcState>((set) => ({
  arcs: [],
  selectedArc: null,
  isLoading: false,
  error: null,
  setArcs: (arcs) => set({ arcs }),
  addArc: (arc) => set((state) => ({ arcs: [...state.arcs, arc] })),
  updateArc: (updatedArc) => set((state) => ({
    arcs: state.arcs.map((arc) => 
      arc.id === updatedArc.id ? updatedArc : arc
    ),
  })),
  deleteArc: (arcId) => set((state) => ({
    arcs: state.arcs.filter((arc) => arc.id !== arcId),
  })),
  setSelectedArc: (arc) => set({ selectedArc: arc }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
})); 