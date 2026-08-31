// Authentication Service simulating future API integration
// Future Endpoint: POST /api/auth/login, POST /api/auth/register

export const authService = {
  login: (email, password) => {
    console.log(`[API Mock Call] POST /api/auth/login`);
    console.log(`Payload:`, { email, password });
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          token: "mock-jwt-token-12345",
          user: {
            name: "Sita Ram",
            email: email,
            userType: "Citizen",
            preferredLanguage: "en"
          }
        });
      }, 500);
    });
  },

  register: (name, email, password, userType, preferredLanguage) => {
    console.log(`[API Mock Call] POST /api/auth/register`);
    console.log(`Payload:`, { name, email, password, userType, preferredLanguage });
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          token: "mock-jwt-token-67890",
          user: {
            name,
            email,
            userType,
            preferredLanguage
          }
        });
      }, 500);
    });
  },

  updateProfile: (name, email, preferredLanguage, userType) => {
    console.log(`[API Mock Call] PUT /api/auth/profile`);
    console.log(`Payload:`, { name, email, preferredLanguage, userType });
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          user: {
            name,
            email,
            preferredLanguage,
            userType
          }
        });
      }, 300);
    });
  }
};
