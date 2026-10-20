import { useQuery } from '@tanstack/react-query'
import { fetchHealth } from '../api/health'

export function HomePage() {
  const { data, isPending, isError } = useQuery({ queryKey: ['health'], queryFn: fetchHealth })

  let label = 'Checking API…'
  if (isError) label = 'API unreachable'
  else if (data) label = data.status === 'ok' ? 'API is healthy' : 'API is degraded (database down)'

  return (
    <section>
      <h1 className="text-2xl font-semibold">Exam Platform</h1>
      <p className="mt-4" role="status" data-pending={isPending}>
        {label}
      </p>
    </section>
  )
}
