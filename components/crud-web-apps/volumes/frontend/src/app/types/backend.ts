import { Params } from '@angular/router';
import { V1PersistentVolumeClaim, V1Pod } from '@kubernetes/client-node';
import { Status, BackendResponse, STATUS_TYPE } from 'kubeflow-aigo';
import { EventObject } from './event';

export interface VWABackendResponse extends BackendResponse {
  pvcs?: PVCResponseObject[];
  pvc?: V1PersistentVolumeClaim;
  events?: EventObject[];
  pods?: V1Pod[];
  totalCount?: number;
}

export interface VWAGetPVCsResponse {
  pvcs: PVCResponseObject[];
  totalCount: number;
}

export interface PVCResponseObject {
  age: string;
  capacity: string;
  class: string;
  modes: string[];
  name: string;
  namespace: string;
  status: Status;
  notebooks: string[];
  viewer: {
    status: STATUS_TYPE;
    url: string;
  };
}

export interface PVCProcessedObject extends PVCResponseObject {
  deleteAction?: string;
  editAction?: string;
  closePVCViewerAction?: string;
  openPVCViewerAction?: string;
  link: {
    text: string;
    url: string;
    queryParams?: Params | null;
  };
}

export interface PVCPostObject {
  name: string;
  type: string;
  size: string | number;
  class: string;
  mode: string;
  snapshot: string;
}
