/**
 * 服务模块统一导出
 */

import { apiClient } from './api';
import { extractionService, ExtractionService } from './extractionService';
import { graphService, GraphService } from './graphService';
import { ontologyService, OntologyService } from './ontologyService';

// 重新导出
export { apiClient };
export { extractionService, ExtractionService };
export { graphService, GraphService };
export { ontologyService, OntologyService };

// 导出所有服务实例
export const services = {
  extraction: extractionService,
  graph: graphService,
  ontology: ontologyService,
};

// 默认导出
export default services;