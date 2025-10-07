# Frontend Testing

## Setup

Install test dependencies:

```bash
cd apps/web
npm install --save-dev jest @testing-library/react @testing-library/jest-dom jest-environment-jsdom
```

## Run Tests

```bash
# Run all tests
npm test

# Run in watch mode
npm run test:watch

# Run specific test
npm test ChatInput
```

## Test Files

- `components/ChatInput.test.tsx` - Tests chat input component
- `components/MessageList.test.tsx` - Tests message display
- `lib/api.test.ts` - Tests API calls

## What We Test

✅ User can type and submit queries
✅ Messages display correctly
✅ API calls work
✅ Loading states work
✅ Error handling