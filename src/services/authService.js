// Authentication Service communicating with FastAPI Backend
// Endpoints: POST /api/auth/login, POST /api/auth/register, GET /api/auth/me, PUT /api/auth/profile

const API_BASE = import.meta.env.VITE_API_URL 
  ? `${import.meta.env.VITE_API_URL.replace(/\/$/, '')}/api/auth` 
  : '/api/auth';

const getUrl = (path) => `${API_BASE}${path}`;

export const authService = {
  /**
   * Log in user with identifier (email OR phone) and password
   */
  login: async (identifier, password) => {
    try {
      const response = await fetch(getUrl('/login'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          identifier: identifier.trim(),
          password,
        }),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const errorMsg = data.detail || data.message || 'Authentication failed. Please check credentials.';
        throw new Error(errorMsg);
      }

      return data;
    } catch (error) {
      console.error('[authService] login error:', error);
      throw error;
    }
  },

  /**
   * Register new user with name, unique email, unique phone, and password
   */
  register: async ({ name, email, phone, password, userType = 'Citizen', preferredLanguage = 'en' }) => {
    try {
      const response = await fetch(getUrl('/register'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: name.trim(),
          email: email.trim(),
          phone: phone.trim(),
          password,
          userType,
          preferredLanguage,
        }),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const errorMsg = data.detail || data.message || 'Registration failed. Please check your information.';
        throw new Error(errorMsg);
      }

      return data;
    } catch (error) {
      console.error('[authService] register error:', error);
      throw error;
    }
  },

  /**
   * Fetch authenticated user details with JWT token
   */
  getMe: async (token) => {
    try {
      const response = await fetch(getUrl('/me'), {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.detail || data.message || 'Session expired or invalid.');
      }

      return data;
    } catch (error) {
      console.error('[authService] getMe error:', error);
      throw error;
    }
  },

  /**
   * Update profile details (name, email, phone, preferredLanguage, userType)
   */
  updateProfile: async ({ name, email, phone, preferredLanguage, userType }, token) => {
    try {
      const response = await fetch(getUrl('/profile'), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: name?.trim(),
          email: email?.trim(),
          phone: phone?.trim(),
          preferredLanguage,
          userType,
        }),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const errorMsg = data.detail || data.message || 'Failed to update profile.';
        throw new Error(errorMsg);
      }

      return data;
    } catch (error) {
      console.error('[authService] updateProfile error:', error);
      throw error;
    }
  },
};

export default authService;
