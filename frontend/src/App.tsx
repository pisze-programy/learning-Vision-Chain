import { useState, ChangeEvent } from 'react';

interface AgentLog {
  node: string;
  data: {
    status?: string;
    [key: string]: any;
  };
  task_id: string;
}

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "success">("idle");
  const [logs, setLogs] = useState<AgentLog[]>([]);
  const [currentNode, setCurrentNode] = useState<string | null>(null);

  async function* parseServerSentEvents(stream: ReadableStream<Uint8Array>): AsyncGenerator<AgentLog, void, unknown> {
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    // Wykorzystanie natywnego Async Iteratora zamiast .getReader() i pętli while
    for await (const chunk of stream as any) {
      buffer += decoder.decode(chunk, { stream: true });
      const parts = buffer.split("\n\n");
      buffer = parts.pop() || "";

      for (const part of parts) {
        const line = part.trim();
        if (line.startsWith("data: ")) {
          try {
            const jsonString = line.replace("data: ", "");
            if (jsonString) {
              yield JSON.parse(jsonString);
            }
          } catch (e) {
            console.error("STREAM_LINE_PARSE_ERROR", e);
          }
        }
      }
    }
  }

  const onFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
      setPreview(URL.createObjectURL(selected));
      setStatus("idle");
      setLogs([]);
      setCurrentNode(null);
    }
  };

  const upload = async () => {
    if (!file) return;

    setStatus("uploading");
    setLogs([]);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok || !response.body) {
        throw new Error("NETWORK_RESPONSE_NOT_OK");
      }

      for await (const log of parseServerSentEvents(response.body)) {
        setCurrentNode(log.node);
        setLogs((prev) => [...prev, log]);
      }

      setStatus("success");
      setCurrentNode(null);

    } catch (error) {
      console.error(error);
      setStatus("idle");
      setCurrentNode(null);
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

        {logs.length > 0 && (
          <div className="border border-slate-100 rounded-xl p-4 bg-slate-50 font-mono text-xs space-y-2 max-h-48 overflow-y-auto">
            Active Node: {currentNode || "Initializing..."}

            <div className="text-slate-400 border-b border-slate-200 pb-1 font-sans font-semibold">
              Agent Execution Steps:
            </div>
            {logs.map((log, index) => (
              <div key={index} className="flex flex-col gap-0.5 border-b border-slate-100 last:border-0 pb-1">
                <span className="text-blue-600 font-bold">[{log.node}]</span>
                <span className="text-slate-700">{log.data.status || JSON.stringify(log.data)}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}