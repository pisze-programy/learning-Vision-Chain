import { useState, ChangeEvent } from 'react';

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "success">("idle");

  const onFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
      setPreview(URL.createObjectURL(selected));
      setStatus("idle");
    }
  };

  const upload = async () => {
    if (!file) return;

    setStatus("uploading");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });
      if (response.ok) setStatus("success");
    } catch (error) {
      console.error(error);
      setStatus("idle");
    }
  };

  return (
    <div className="min-h-screen bg-white text-slate-900 flex flex-col items-center justify-center p-6 font-sans">
      <div className="w-full max-w-lg space-y-8">
        <div className={`relative aspect-video w-full rounded-xl border-2 border-dashed transition-all duration-500 overflow-hidden ${
          status === "uploading" ? "border-blue-500 scale-[0.98] opacity-50" : "border-slate-200"
        }`}>
          {preview ? (
            <img src={preview} className="h-full w-full object-contain" alt="Preview" />
          ) : (
            <div className="flex h-full items-center justify-center text-slate-400">
              No image selected
            </div>
          )}
          <input
            type="file"
            onChange={onFileChange}
            className="absolute inset-0 opacity-0 cursor-pointer"
          />
        </div>

        <div className="space-y-4">
          <button
            onClick={upload}
            disabled={status === "uploading" || !file}
            className="w-full bg-slate-900 text-white font-medium py-3 rounded-lg hover:bg-slate-800 disabled:bg-slate-200 disabled:text-slate-500 transition-all relative overflow-hidden"
          >
            {status === "uploading" ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Processing
              </span>
            ) : status === "success" ? (
              "Done"
            ) : (
              "UPLOAD"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}