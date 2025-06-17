import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// 各テスト後にクリーンアップ
afterEach(() => {
  cleanup();
});

// matchMediaのモック
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // Deprecated
    removeListener: vi.fn(), // Deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// ResizeObserverのモック
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// DOM scrollTo メソッドのモック
Object.defineProperty(HTMLDivElement.prototype, 'scrollTo', {
  value: vi.fn(),
  writable: true,
});

Object.defineProperty(HTMLDivElement.prototype, 'scrollHeight', {
  value: 1000,
  writable: true,
});

// グローバルモック設定
vi.mock('nanoid', () => ({
  nanoid: () => 'test-id-12345',
}));
