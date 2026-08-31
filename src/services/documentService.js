// Document Service simulating future API integration
// Future Endpoint: GET /api/documents/processes

import { documentGuidanceData } from '../data/mockData';

export const documentService = {
  getProcesses: () => {
    console.log(`[API Mock Call] GET /api/documents/processes`);
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(documentGuidanceData);
      }, 300);
    });
  },

  getProcessDetails: (id) => {
    console.log(`[API Mock Call] GET /api/documents/processes/${id}`);
    return new Promise((resolve) => {
      setTimeout(() => {
        const details = documentGuidanceData.find(p => p.id === id);
        resolve(details || null);
      }, 200);
    });
  }
};
