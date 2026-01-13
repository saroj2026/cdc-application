/**
 * Auth Redux slice
 */
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiClient } from '@/lib/api/client';

interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  roles: Array<{ id: number; name: string }>;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// Helper to safely get from localStorage
const getInitialToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  try {
    return localStorage.getItem('access_token');
  } catch {
    return null;
  }
};

// Helper to safely get user from localStorage
const getInitialUser = (): User | null => {
  if (typeof window === 'undefined') return null;
  try {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      return JSON.parse(userStr);
    }
  } catch {
    return null;
  }
  return null;
};

const initialState: AuthState = {
  user: getInitialUser(),
  token: getInitialToken(),
  isAuthenticated: !!getInitialToken(),
  isLoading: false,
  error: null,
};

// Async thunks
export const login = createAsyncThunk(
  'auth/login',
  async ({ email, password }: { email: string; password: string }, { rejectWithValue }) => {
    try {
      // Step 1: Login and get token
      const data = await apiClient.login(email, password);
      
      if (!data.access_token) {
        return rejectWithValue('No access token received from server');
      }
      
      // Step 2: Set token in API client and localStorage
      apiClient.setToken(data.access_token);
      
      // Step 3: Wait a bit to ensure token is set, then get user info
      // Small delay to ensure localStorage is updated
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Step 4: Get current user info
      try {
        const user = await apiClient.getCurrentUser();
        return { token: data.access_token, user };
      } catch (userError: any) {
        // If getting user fails, still return the token
        // User info can be fetched later
        console.warn('Failed to fetch user info after login:', userError);
        return { 
          token: data.access_token, 
          user: { email, id: 0, full_name: email, is_active: true, is_superuser: false, roles: [] } 
        };
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Login failed';
      return rejectWithValue(errorMessage);
    }
  }
);

export const logout = createAsyncThunk('auth/logout', async () => {
  await apiClient.logout();
});

export const getCurrentUser = createAsyncThunk('auth/getCurrentUser', async (_, { rejectWithValue }) => {
  try {
    const user = await apiClient.getCurrentUser();
    console.log('[Auth] getCurrentUser response:', {
      email: user?.email,
      is_superuser: user?.is_superuser,
      full_user: user
    });
    
    // Validate that is_superuser is a boolean
    if (user && typeof user.is_superuser !== 'boolean') {
      console.warn('[Auth] is_superuser is not a boolean, defaulting to false. User data:', user);
      user.is_superuser = false;
    }
    
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(user));
    }
    return user;
  } catch (error: any) {
    console.error('[Auth] Failed to fetch current user:', error);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('user');
      localStorage.removeItem('access_token');
    }
    return rejectWithValue(error.response?.data?.detail || 'Failed to fetch user info');
  }
});

export const createUser = createAsyncThunk(
  'auth/createUser',
  async (userData: { full_name: string; email: string; password: string }, { rejectWithValue }) => {
    try {
      const user = await apiClient.createUser(userData);
      return user;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create account');
    }
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.isLoading = false;
        state.token = action.payload.token;
        state.user = action.payload.user;
        state.isAuthenticated = true;
        if (typeof window !== 'undefined') {
          localStorage.setItem('user', JSON.stringify(action.payload.user));
        }
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Logout
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
        if (typeof window !== 'undefined') {
          localStorage.removeItem('user');
        }
      })
      // Get current user
      .addCase(getCurrentUser.fulfilled, (state, action) => {
        const userData = action.payload;
        // Ensure is_superuser is properly set
        if (userData && typeof userData.is_superuser === 'boolean') {
          state.user = userData;
        } else {
          // If is_superuser is missing or invalid, set it to false and log warning
          console.warn('[Auth] User data missing is_superuser, setting to false:', userData);
          state.user = userData ? { ...userData, is_superuser: false } : null;
        }
        state.isAuthenticated = true;
        if (typeof window !== 'undefined' && userData) {
          localStorage.setItem('user', JSON.stringify(state.user));
        }
      })
      .addCase(getCurrentUser.rejected, (state, action) => {
        // Don't clear user data on error - keep cached user if available
        // Only clear if it's an authentication error
        const error = action.payload as any;
        const isAuthError = error?.response?.status === 401 || error?.response?.status === 403;
        
        if (isAuthError) {
          // Authentication error - clear everything
          state.user = null;
          state.isAuthenticated = false;
          state.token = null;
          if (typeof window !== 'undefined') {
            localStorage.removeItem('user');
            localStorage.removeItem('access_token');
          }
        } else {
          // Other errors (network, server) - keep cached user data
          console.warn('[Auth] getCurrentUser failed but keeping cached user data:', error);
          // Don't clear state - keep existing user data
        }
      })
      // Create user
      .addCase(createUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createUser.fulfilled, (state) => {
        state.isLoading = false;
        // User created successfully, redirect to login
      })
      .addCase(createUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError } = authSlice.actions;
export default authSlice.reducer;

