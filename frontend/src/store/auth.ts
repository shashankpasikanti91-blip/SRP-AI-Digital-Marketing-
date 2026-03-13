import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Tenant } from '@/types'

interface AuthState {
  token: string | null
  tenant: Tenant | null
  _hasHydrated: boolean
  setAuth: (token: string, tenant: Tenant) => void
  logout: () => void
  setHasHydrated: (state: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      tenant: null,
      _hasHydrated: false,
      setAuth: (token, tenant) => set({ token, tenant }),
      logout: () => set({ token: null, tenant: null }),
      setHasHydrated: (state) => set({ _hasHydrated: state }),
    }),
    {
      name: 'srp-auth',
      partialize: (state) => ({ token: state.token, tenant: state.tenant }),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true)
      },
    }
  )
)
