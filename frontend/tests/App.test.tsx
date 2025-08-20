import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from '../src/App'

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    // Basic test to ensure the app renders
    expect(document.body).toBeInTheDocument()
  })
})
