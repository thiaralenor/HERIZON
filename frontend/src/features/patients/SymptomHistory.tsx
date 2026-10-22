import { useEffect, useState } from 'react'
import { listSymptoms, addSymptom, deleteSymptom, SymptomLog } from './api'

export function SymptomHistory() {
  const [logs, setLogs] = useState<SymptomLog[]>([])
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState<string | null>(null)

  // add-form state
  const [symptoms, setSymptoms] = useState('')
  const [severity, setSeverity] = useState<string>('')
  const [saving, setSaving] = useState(false)
  const [formErr, setFormErr] = useState<string | null>(null)

  async function refresh() {
    setLoading(true)
    setErr(null)
    try {
      const data = await listSymptoms()
      setLogs(data)
    } catch (e: any) {
      setErr(e.message ?? 'Failed to load symptoms')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setFormErr(null)
    if (!symptoms.trim()) {
      setFormErr('Please describe your symptoms.')
      return
    }
    const sev = severity === '' ? undefined : Number(severity)
    if (sev != null && (sev < 1 || sev > 10)) {
      setFormErr('Severity must be between 1 and 10.')
      return
    }

    setSaving(true)
    try {
      const created = await addSymptom(symptoms.trim(), sev)
      setLogs((prev) => [created, ...prev])
      setSymptoms('')
      setSeverity('')
    } catch (e: any) {
      setFormErr(e.message ?? 'Failed to save symptom log')
    } finally {
      setSaving(false)
    }
  }

  async function onDelete(id: string) {
    if (!confirm('Delete this log? This cannot be undone.')) return
    const prev = logs
    setLogs((l) => l.filter((x) => x.id !== id))     // optimistic
    try {
      await deleteSymptom(id)
    } catch (e: any) {
      setLogs(prev)                                   // rollback
      setErr(e.message ?? 'Failed to delete log')
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">My symptoms</h1>
        <p className="text-sm text-stone-600 mt-1">
          Private to you. No doctor can see these entries.
        </p>
      </div>

      {/* Add form */}
      <form
        onSubmit={onSubmit}
        className="bg-white rounded-xl border border-stone-200 p-5 space-y-3"
      >
        <label className="block">
          <span className="text-sm font-medium">What are you experiencing?</span>
          <textarea
            className="w-full border rounded p-2 mt-1"
            rows={3}
            maxLength={2000}
            placeholder="e.g. persistent headache, mild fever since yesterday"
            value={symptoms}
            onChange={(e) => setSymptoms(e.target.value)}
          />
        </label>

        <label className="block">
          <span className="text-sm font-medium">
            Severity (1 = mild, 10 = severe) — optional
          </span>
          <input
            type="number"
            min={1}
            max={10}
            className="w-32 border rounded p-2 mt-1"
            value={severity}
            onChange={(e) => setSeverity(e.target.value)}
          />
        </label>

        {formErr && <div className="text-red-600 text-sm">{formErr}</div>}

        <button
          type="submit"
          disabled={saving}
          className="bg-kam-teal text-white rounded px-4 py-2 disabled:opacity-50"
        >
          {saving ? 'Saving…' : 'Save entry'}
        </button>
      </form>

      {/* List */}
      {loading ? (
        <div className="text-stone-500">Loading…</div>
      ) : err ? (
        <div className="bg-red-50 border border-red-200 text-red-800 rounded-xl p-4 text-sm">
          <div className="font-medium mb-1">Could not load symptoms</div>
          <div>{err}</div>
          <button
            onClick={refresh}
            className="mt-2 underline text-red-800"
          >
            Try again
          </button>
        </div>
      ) : logs.length === 0 ? (
        <div className="bg-white rounded-xl border border-stone-200 p-8 text-center text-stone-600">
          No symptom entries yet. Use the form above to log one.
        </div>
      ) : (
        <div className="space-y-3">
          {logs.map((log) => (
            <div
              key={log.id}
              className="bg-white rounded-xl border border-stone-200 p-4"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="text-sm text-stone-500 mb-1">
                    {new Date(log.logged_at).toLocaleString()}
                  </div>
                  <div className="whitespace-pre-line">{log.symptoms}</div>
                  {log.severity != null && (
                    <div className="mt-2 text-xs">
                      <span className="bg-amber-100 text-amber-800 px-2 py-0.5 rounded">
                        Severity {log.severity}/10
                      </span>
                    </div>
                  )}
                </div>
                <button
                  onClick={() => onDelete(log.id)}
                  className="text-xs text-red-600 hover:underline shrink-0"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}