/**
 * ChatInput Component Tests
 *
 * Run with: npm test ChatInput
 */

import { render, screen, fireEvent } from '@testing-library/react'
import ChatInput from '@/components/ChatInput'

describe('ChatInput Component', () => {
  test('renders input field and submit button', () => {
    const mockOnSubmit = jest.fn()
    render(<ChatInput onSubmit={mockOnSubmit} isLoading={false} />)

    // Check if input exists
    const input = screen.getByPlaceholderText(/ask a question/i)
    expect(input).toBeInTheDocument()

    // Check if submit button exists
    const button = screen.getByRole('button')
    expect(button).toBeInTheDocument()
  })

  test('calls onSubmit with query text when submitted', () => {
    const mockOnSubmit = jest.fn()
    render(<ChatInput onSubmit={mockOnSubmit} isLoading={false} />)

    const input = screen.getByPlaceholderText(/ask a question/i)
    const button = screen.getByRole('button')

    // Type query
    fireEvent.change(input, { target: { value: 'How do I deploy Atlas?' } })

    // Submit
    fireEvent.click(button)

    // Verify callback was called with correct value
    expect(mockOnSubmit).toHaveBeenCalledWith('How do I deploy Atlas?')
  })

  test('does not submit empty query', () => {
    const mockOnSubmit = jest.fn()
    render(<ChatInput onSubmit={mockOnSubmit} isLoading={false} />)

    const button = screen.getByRole('button')

    // Try to submit without typing
    fireEvent.click(button)

    // Should not call onSubmit
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  test('disables submit button when loading', () => {
    const mockOnSubmit = jest.fn()
    render(<ChatInput onSubmit={mockOnSubmit} isLoading={true} />)

    const button = screen.getByRole('button')

    // Button should be disabled
    expect(button).toBeDisabled()
  })

  test('clears input after submission', () => {
    const mockOnSubmit = jest.fn()
    render(<ChatInput onSubmit={mockOnSubmit} isLoading={false} />)

    const input = screen.getByPlaceholderText(/ask a question/i) as HTMLInputElement
    const button = screen.getByRole('button')

    // Type and submit
    fireEvent.change(input, { target: { value: 'Test query' } })
    fireEvent.click(button)

    // Input should be cleared
    expect(input.value).toBe('')
  })
})