// Legal Resource Service simulating future API integration
// Future Endpoint: GET /api/resources?search=...&category=...

import { legalResources } from '../data/mockData';

export const resourceService = {
  searchResources: (query = "", category = "All") => {
    console.log(`[API Mock Call] GET /api/resources?search=${query}&category=${category}`);
    
    return new Promise((resolve) => {
      setTimeout(() => {
        let results = legalResources;
        
        if (category && category !== "All") {
          results = results.filter(r => r.category.toLowerCase() === category.toLowerCase());
        }
        
        if (query) {
          const lowerQuery = query.toLowerCase();
          results = results.filter(r => 
            r.title.toLowerCase().includes(lowerQuery) || 
            r.description.toLowerCase().includes(lowerQuery) ||
            r.overview.toLowerCase().includes(lowerQuery)
          );
        }
        
        resolve(results);
      }, 300);
    });
  },

  getResourceById: (id) => {
    console.log(`[API Mock Call] GET /api/resources/${id}`);
    
    return new Promise((resolve) => {
      setTimeout(() => {
        const resource = legalResources.find(r => r.id === id);
        resolve(resource || null);
      }, 200);
    });
  }
};
