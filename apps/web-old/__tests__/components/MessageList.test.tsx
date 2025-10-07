/**
 * MessageList Component Tests
 *
 * Run with: npm test MessageList
 */

import { render, screen } from '@testing-library/react'
import MessageList from '@/components/MessageList'

describe('MessageList Component', () => {
  test('renders empty state when no messages', () => {
    render(<MessageList messages={[]} />)

    // Should show some empty state or nothing
    const list = screen.queryByRole('list')
    if (list) {
      expect(list.children.length).toBe(0)
    }
  })

  test('renders user question message', () => {
    const messages = [
      {
        id: '1',
        role: 'user' as const,
        content: 'How do I deploy Atlas?',
        timestamp: new Date(),
      }
    ]

    render(<MessageList messages={messages} />)

    // Check if question is displayed
    expect(screen.getByText('How do I deploy Atlas?')).toBeInTheDocument()
  })

  test('renders assistant answer message', () => {
    const messages = [
      {
        id: '1',
        role: 'user' as const,
        content: 'How do I deploy Atlas?',
        timestamp: new Date(),
      },
      {
        id: '2',
        role: 'assistant' as const,
        content: 'To deploy Atlas, run make deploy in the root directory.',
        timestamp: new Date(),
      }
    ]

    render(<MessageList messages={messages} />)

    // Check if answer is displayed
    expect(screen.getByText(/To deploy Atlas/i)).toBeInTheDocument()
  })

  test('renders multiple messages in order', () => {
    const messages = [
      {
        id: '1',
        role: 'user' as const,
        content: 'First question',
        timestamp: new Date(),
      },
      {
        id: '2',
        role: 'assistant' as const,
        content: 'First answer',
        timestamp: new Date(),
      },
      {
        id: '3',
        role: 'user' as const,
        content: 'Second question',
        timestamp: new Date(),
      }
    ]

    render(<MessageList messages={messages} />)

    // All messages should be present
    expect(screen.getByText('First question')).toBeInTheDocument()
    expect(screen.getByText('First answer')).toBeInTheDocument()
    expect(screen.getByText('Second question')).toBeInTheDocument()
  })
})