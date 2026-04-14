import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus, Trash2, CheckCircle, Clock, Activity } from 'lucide-react'
import client from '../api/client'

interface MonitoringTask {
  id: number
  task_type: string
  schedule: string | null
  is_active: boolean
  last_run: string | null
  created_at: string
}

const TASK_TYPES = ['scan_local_folder', 'run_scheduled_search', 'monitor_domain', 'monitor_ip']

export default function MonitoringPage() {
  const { t } = useTranslation()
  const [tasks, setTasks] = useState<MonitoringTask[]>([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({ task_type: 'scan_local_folder', schedule: '0 * * * *', config_json: '' })
  const [adding, setAdding] = useState(false)

  const fetchTasks = async () => {
    try {
      const res = await client.get('/monitoring')
      setTasks(res.data || [])
    } catch {
      setTasks([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchTasks() }, [])

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault()
    setAdding(true)
    try {
      await client.post('/monitoring', form)
      fetchTasks()
    } finally {
      setAdding(false)
    }
  }

  const handleDelete = async (id: number) => {
    await client.delete(`/monitoring/${id}`)
    fetchTasks()
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold" style={{ color: '#e0e8f0' }}>
          {t('monitoring.title')}
        </h1>
        <p className="text-sm mt-1" style={{ color: '#4a6080' }}>
          {t('monitoring.subtitle')}
        </p>
      </div>

      {/* Add task */}
      <div className="p-5 rounded-2xl border" style={{ background: '#0f1729', borderColor: '#1e3a5f' }}>
        <h2 className="text-sm font-semibold mb-3" style={{ color: '#8099b3' }}>
          {t('monitoring.addTask')}
        </h2>
        <form onSubmit={handleAdd} className="flex gap-3">
          <select
            value={form.task_type}
            onChange={(e) => setForm({ ...form, task_type: e.target.value })}
            className="flex-1 px-3 py-2 rounded-lg border text-sm outline-none"
            style={{ background: '#1a2340', borderColor: '#1e3a5f', color: '#e0e8f0' }}
          >
            {TASK_TYPES.map((taskType) => <option key={taskType} value={taskType}>{taskType}</option>)}
          </select>
          <input
            type="text"
            placeholder="Cron schedule (e.g. 0 * * * *)"
            value={form.schedule}
            onChange={(e) => setForm({ ...form, schedule: e.target.value })}
            className="flex-1 px-3 py-2 rounded-lg border text-sm outline-none font-mono"
            style={{ background: '#1a2340', borderColor: '#1e3a5f', color: '#e0e8f0' }}
          />
          <button
            type="submit"
            disabled={adding}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium"
            style={{ background: '#00ff88', color: '#000' }}
          >
            <Plus size={14} />
            {t('common.add')}
          </button>
        </form>
        <p className="text-xs mt-2" style={{ color: '#4a6080' }}>
          {t('monitoring.phase2')}
        </p>
      </div>

      {/* Task list */}
      <div className="p-5 rounded-2xl border" style={{ background: '#0f1729', borderColor: '#1e3a5f' }}>
        {loading ? (
          <p className="text-sm" style={{ color: '#4a6080' }}>{t('common.loading')}</p>
        ) : tasks.length === 0 ? (
          <div className="text-center py-8" style={{ color: '#4a6080' }}>
            <Activity size={32} className="mx-auto mb-2 opacity-30" />
            <p className="text-sm">{t('monitoring.noTasks')}</p>
          </div>
        ) : (
          <div className="space-y-2">
            {tasks.map((task) => (
              <div
                key={task.id}
                className="flex items-center justify-between p-3 rounded-lg border"
                style={{ borderColor: '#1e3a5f', background: '#1a2340' }}
              >
                <div className="flex items-center gap-3">
                  {task.is_active ? (
                    <CheckCircle size={14} style={{ color: '#00ff88' }} />
                  ) : (
                    <Clock size={14} style={{ color: '#4a6080' }} />
                  )}
                  <span className="text-sm font-mono font-medium" style={{ color: '#e0e8f0' }}>
                    {task.task_type}
                  </span>
                  {task.schedule && (
                    <span className="text-xs font-mono px-2 py-0.5 rounded" style={{ background: '#0f1729', color: '#00d4ff' }}>
                      {task.schedule}
                    </span>
                  )}
                  {task.last_run && (
                    <span className="text-xs" style={{ color: '#4a6080' }}>
                      Last: {new Date(task.last_run).toLocaleDateString()}
                    </span>
                  )}
                </div>
                <button
                  onClick={() => handleDelete(task.id)}
                  style={{ color: '#ff3366' }}
                  className="p-1.5 rounded"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
