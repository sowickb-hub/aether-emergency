import { useRef, useState, useCallback, type DragEvent, type ChangeEvent } from 'react';
import { motion } from 'framer-motion';
import { Zap, UploadCloud, X, FileImage, Loader2 } from 'lucide-react';
import type { ImagePayload } from '../types';

interface InputChamberProps {
  onAnalyze: (text: string, images: ImagePayload[]) => void;
  isLoading: boolean;
  onReset: () => void;
}

interface PreviewImage {
  name: string;
  mime_type: string;
  data: string;       // base64
  previewUrl: string; // object URL for <img>
}

export default function InputChamber({ onAnalyze, isLoading, onReset }: InputChamberProps) {
  const [text, setText]           = useState('');
  const [images, setImages]       = useState<PreviewImage[]>([]);
  const [isDragOver, setDragOver] = useState(false);
  const fileInputRef              = useRef<HTMLInputElement>(null);

  /* ── File → base64 helper ─────────────────────── */
  const fileToPayload = (file: File): Promise<PreviewImage> =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        const base64 = result.split(',')[1];
        resolve({
          name: file.name,
          mime_type: file.type,
          data: base64,
          previewUrl: URL.createObjectURL(file),
        });
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });

  const addFiles = useCallback(async (files: FileList | File[]) => {
    const arr = Array.from(files).filter(f => f.type.startsWith('image/')).slice(0, 5);
    const payloads = await Promise.all(arr.map(fileToPayload));
    setImages(prev => [...prev, ...payloads].slice(0, 5));
  }, []);

  const removeImage = (idx: number) => {
    setImages(prev => {
      URL.revokeObjectURL(prev[idx].previewUrl);
      return prev.filter((_, i) => i !== idx);
    });
  };

  /* ── Drag & Drop ──────────────────────────────── */
  const onDragOver  = (e: DragEvent) => { e.preventDefault(); setDragOver(true); };
  const onDragLeave = ()             => setDragOver(false);
  const onDrop      = (e: DragEvent) => {
    e.preventDefault(); setDragOver(false);
    if (e.dataTransfer.files.length) addFiles(e.dataTransfer.files);
  };

  /* ── File input ───────────────────────────────── */
  const onFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.length) addFiles(e.target.files);
    e.target.value = '';
  };

  /* ── Submit ───────────────────────────────────── */
  const handleSubmit = () => {
    if (!text.trim() || isLoading) return;
    onAnalyze(text, images.map(({ mime_type, data }) => ({ mime_type, data })));
  };

  const handleReset = () => {
    setText('');
    images.forEach(img => URL.revokeObjectURL(img.previewUrl));
    setImages([]);
    onReset();
  };

  return (
    <section
      aria-label="Crisis Input Chamber"
      className="h-full flex flex-col gap-5 p-8"
    >
      {/* ── Header ── */}
      <div>
        <p className="section-label">Input Chamber</p>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight text-gray-900">
          Crisis Report
        </h1>
        <p className="mt-1 text-xs text-gray-400 leading-relaxed">
          Describe the emergency scenario. Attach evidence photos for multimodal analysis.
        </p>
      </div>

      {/* ── Textarea ── */}
      <div className="flex-1 flex flex-col min-h-0">
        <label htmlFor="crisis-input" className="section-label mb-2">
          Unstructured Crisis Data
        </label>
        <textarea
          id="crisis-input"
          aria-label="Crisis report text input"
          className="aether-emergency-textarea flex-1 p-4 min-h-0"
          placeholder={
            "Paste crisis report here…\n\nExample: Smoke and fire on the 3rd floor of Pine Ave building 7. Two people trapped, one unconscious. Electrical sparks near stairwell. Crowd gathering outside…"
          }
          value={text}
          onChange={e => setText(e.target.value)}
          disabled={isLoading}
          spellCheck
        />
      </div>

      {/* ── Drop Zone ── */}
      <div>
        <label className="section-label mb-2 block">Drop Evidence</label>
        <div
          role="button"
          aria-label="Upload evidence images — click or drag and drop"
          tabIndex={0}
          className={`drop-zone p-5 gap-1 ${isDragOver ? 'drag-over' : ''}`}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          onClick={() => fileInputRef.current?.click()}
          onKeyDown={e => e.key === 'Enter' && fileInputRef.current?.click()}
        >
          <UploadCloud size={22} className="text-gray-400" />
          <span className="text-xs text-gray-500 font-medium">
            Click or drag &amp; drop images
          </span>
          <span className="text-[10px] text-gray-400">JPG, PNG, WEBP — up to 5</span>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          multiple
          className="hidden"
          aria-label="Evidence image file input"
          onChange={onFileChange}
        />

        {/* Image Previews */}
        {images.length > 0 && (
          <div className="mt-3 flex gap-2 flex-wrap">
            {images.map((img, idx) => (
              <div key={idx} className="relative group">
                <img
                  src={img.previewUrl}
                  alt={`Evidence ${idx + 1}: ${img.name}`}
                  className="w-14 h-14 object-cover rounded-lg border border-gray-200"
                />
                <button
                  onClick={() => removeImage(idx)}
                  aria-label={`Remove image ${img.name}`}
                  className="absolute -top-1.5 -right-1.5 bg-gray-800 text-white rounded-full p-0.5
                             opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <X size={10} />
                </button>
                <div
                  className="absolute bottom-0 left-0 right-0 bg-gray-800/60 rounded-b-lg
                             flex items-center justify-center py-0.5"
                >
                  <FileImage size={8} className="text-white" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Actions ── */}
      <div className="flex flex-col gap-2">
        <motion.button
          id="analyze-btn"
          aria-label="Analyze crisis report and dispatch intelligence"
          className="btn-primary"
          onClick={handleSubmit}
          disabled={!text.trim() || isLoading}
          whileTap={{ scale: 0.98 }}
        >
          {isLoading ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              Analyzing…
            </>
          ) : (
            <>
              <Zap size={16} />
              Analyze &amp; Dispatch
            </>
          )}
        </motion.button>

        {isLoading && (
          <button
            onClick={handleReset}
            className="text-xs text-gray-400 hover:text-gray-600 transition-colors text-center py-1"
            aria-label="Cancel current analysis"
          >
            Cancel
          </button>
        )}
      </div>
    </section>
  );
}
