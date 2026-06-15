import { create } from 'zustand';

type AuthState = {
  token: string | null;
  setToken: (token: string | null) => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('clausemind_token'),
  setToken: (token) => {
    if (token) {
      localStorage.setItem('clausemind_token', token);
    } else {
      localStorage.removeItem('clausemind_token');
    }
    set({ token });
  },
}));
