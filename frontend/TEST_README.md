# Frontend Testing Guide

## Overview

This frontend project uses **Vitest** for unit and component testing, along with **React Testing Library** for component testing best practices.

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

## Test Structure

```
src/
├── test/
│   ├── setup.ts          # Test setup and global mocks
│   ├── utils.tsx         # Custom render functions
│   └── mocks.ts          # Mock data
└── components/
    └── common/
        ├── Button.tsx
        └── __tests__/
            └── Button.test.tsx
```

## Test Coverage

### Common Components
- ✅ **Button** - All variants, sizes, states, and click handling
- ✅ **Card** - Glass effect, hover states, padding options
- ✅ **Badge** - All status variants, colors, sizes, and icons
- ✅ **Loading** - Spinner rendering, text display, fullScreen mode
- ✅ **Input** - (To be implemented)
- ✅ **Modal** - (To be implemented)

### Dashboard Components
- ✅ **StatsCard** - Title, value, icon, trend indicators, color variants

### Layout Components
- ⏳ **Header** - (To be implemented)
- ⏳ **Sidebar** - (To be implemented)
- ⏳ **Layout** - (To be implemented)

### Pages
- ⏳ **DashboardPage** - (To be implemented)
- ⏳ **AgentConfigPage** - (To be implemented)
- ⏳ **TriggerCallPage** - (To be implemented)
- ⏳ **CallHistoryPage** - (To be implemented)
- ⏳ **CallDetailsPage** - (To be implemented)

## Writing Tests

### Basic Component Test

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '../../../test/utils';
import { YourComponent } from '../YourComponent';

describe('YourComponent', () => {
  it('renders correctly', () => {
    render(<YourComponent />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });
});
```

### Testing User Interactions

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '../../../test/utils';
import userEvent from '@testing-library/user-event';
import { YourComponent } from '../YourComponent';

describe('YourComponent', () => {
  it('handles click events', async () => {
    const handleClick = vi.fn();
    const user = userEvent.setup();

    render(<YourComponent onClick={handleClick} />);
    await user.click(screen.getByRole('button'));

    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### Testing with Mock Data

```typescript
import { mockCall, mockAgentConfig } from '../../../test/mocks';

describe('YourComponent', () => {
  it('displays call data', () => {
    render(<YourComponent call={mockCall} />);
    expect(screen.getByText(mockCall.driver_name)).toBeInTheDocument();
  });
});
```

## Best Practices

1. **Use `screen` queries** - Prefer `screen.getByText()` over container queries
2. **Test user behavior** - Test from the user's perspective, not implementation details
3. **Use semantic queries** - Prefer `getByRole`, `getByLabelText` over `getByTestId`
4. **Mock external dependencies** - Mock API calls, routers, and external libraries
5. **Keep tests focused** - One assertion per test when possible
6. **Use descriptive test names** - Clearly describe what is being tested

## Mocking

### Mock API Calls

```typescript
import { vi } from 'vitest';
import { api } from '../services/api';

vi.mock('../services/api', () => ({
  api: {
    getAgentConfigs: vi.fn().mockResolvedValue([mockAgentConfig]),
    createCall: vi.fn().mockResolvedValue({ call_id: '123' }),
  },
}));
```

### Mock React Router

The custom render function in `test/utils.tsx` automatically wraps components with `BrowserRouter`.

## Common Issues

### Issue: Tests fail with "Cannot find module"
**Solution**: Check import paths and ensure vitest.config.ts has correct path aliases.

### Issue: "window.matchMedia is not a function"
**Solution**: Already mocked in `test/setup.ts`.

### Issue: CSS imports cause errors
**Solution**: Vitest config has `css: true` to handle CSS imports.

## CI/CD Integration

Add to your CI pipeline:

```yaml
- name: Run tests
  run: npm test -- --run

- name: Generate coverage
  run: npm run test:coverage
```

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
