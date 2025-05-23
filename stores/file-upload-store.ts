import { create } from 'zustand';

interface FileUploadState {
  uploadedFile: File | null;
  isDragging: boolean;
  setUploadedFile: (file: File | null) => void;
  setIsDragging: (isDragging: boolean) => void;
  clearFile: () => void;
}

export const useFileUploadStore = create<FileUploadState>((set) => ({
  uploadedFile: null,
  isDragging: false,
  setUploadedFile: (file) => set({ uploadedFile: file }),
  setIsDragging: (isDragging) => set({ isDragging }),
  clearFile: () => set({ uploadedFile: null }),
}));