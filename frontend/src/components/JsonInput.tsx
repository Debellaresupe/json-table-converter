import { Upload } from "lucide-react";

const MAX_FILE_BYTES = 10 * 1024 * 1024;

type Props = {
  rawJson: string;
  setRawJson: (value: string) => void;
  setError: (value: string) => void;
};

export function JsonInput({ rawJson, setRawJson, setError }: Props) {
  async function readFiles(files: FileList | null) {
    if (!files?.length) return;
    const parsed: unknown[] = [];
    for (const file of Array.from(files)) {
      if (!file.name.endsWith(".json")) {
        setError(`Файл ${file.name} не является .json`);
        return;
      }
      if (file.size > MAX_FILE_BYTES) {
        setError(`Файл ${file.name} слишком большой. Лимит: 10 MB.`);
        return;
      }
      const text = await file.text();
      try {
        parsed.push(JSON.parse(text));
      } catch (e) {
        setError(`Ошибка JSON в ${file.name}: ${(e as Error).message}`);
        return;
      }
    }
    setError("");
    setRawJson(JSON.stringify(files.length === 1 ? parsed[0] : parsed, null, 2));
  }

  return (
    <section className="card input-card">
      <div className="dropzone" onDragOver={(e) => e.preventDefault()} onDrop={(e) => { e.preventDefault(); readFiles(e.dataTransfer.files); }}>
        <Upload size={22} />
        <strong>Перетащите JSON-файл сюда</strong>
        <span>или выберите один/несколько файлов</span>
        <input type="file" accept="application/json,.json" multiple onChange={(e) => readFiles(e.target.files)} />
      </div>
      <textarea value={rawJson} onChange={(e) => setRawJson(e.target.value)} placeholder="Вставьте JSON сюда..." spellCheck={false} />
    </section>
  );
}
