import { create } from 'zustand';

import type { UserInfo } from '../types';

type AuthState = {
  token: string | null;
  user: UserInfo | null;
  setAuth: (token: string, user: UserInfo) => void;
  clearAuth: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('clausemind_token'),
  user: (() => {
    try {
      const raw = localStorage.getItem('clausemind_user');
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  })(),
  setAuth: (token, user) => {
    localStorage.setItem('clausemind_token', token);
    localStorage.setItem('clausemind_user', JSON.stringify(user));
    set({ token, user });
  },
  clearAuth: () => {
    localStorage.removeItem('clausemind_token');
    localStorage.removeItem('clausemind_user');
    set({ token: null, user: null });
  },
}));
