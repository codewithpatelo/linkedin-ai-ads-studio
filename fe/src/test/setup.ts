import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Basic mocks for browser APIs
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn(() => ({
    matches: false,
    addListener: vi.fn(),
    removeListener: vi.fn(),
  })),
})
