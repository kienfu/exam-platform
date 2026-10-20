import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { createMemoryRouter, RouterProvider } from 'react-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fetchHealth } from './api/health'
import { routes } from './routes'

vi.mock('./api/health')

function renderAt(path: string) {
  const router = createMemoryRouter(routes, { initialEntries: [path] })
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(
    <QueryClientProvider client={client}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  )
}

describe('routes', () => {
  beforeEach(() => {
    vi.mocked(fetchHealth).mockReset()
  })

  it('shows a healthy API on the home page', async () => {
    vi.mocked(fetchHealth).mockResolvedValue({ status: 'ok', database: 'ok' })
    renderAt('/')
    expect(await screen.findByText('API is healthy')).toBeInTheDocument()
  })

  it('shows an error when the API is unreachable', async () => {
    vi.mocked(fetchHealth).mockRejectedValue(new Error('network'))
    renderAt('/')
    expect(await screen.findByText('API unreachable')).toBeInTheDocument()
  })

  it('renders the not found page for unknown routes', () => {
    renderAt('/nope')
    expect(screen.getByRole('heading', { name: 'Page not found' })).toBeInTheDocument()
  })
})
