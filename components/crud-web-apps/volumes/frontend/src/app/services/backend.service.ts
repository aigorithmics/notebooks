import { Injectable } from '@angular/core';
import { BackendService, SnackBarService } from 'kubeflow-aigo';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { PVCResponseObject, VWABackendResponse, PVCPostObject, VWAGetPVCsResponse } from '../types';
import { V1PersistentVolumeClaim, V1Pod } from '@kubernetes/client-node';
import { EventObject } from '../types/event';

@Injectable({
  providedIn: 'root',
})
export class VWABackendService extends BackendService {
  constructor(public http: HttpClient, public snackBar: SnackBarService) {
    super(http, snackBar);
  }

  private getNamespacedPVCs(
    namespace: string,
    limit?: number,
    page?: number,
    sortBy?: string,
    sortDirection?: string,
    filterBy?: string,
  ): Observable<VWAGetPVCsResponse> {
    const url = `api/namespaces/${namespace}/pvcs`;
    let params = new HttpParams();
    if (limit !== undefined) { params = params.append('limit', limit.toString()); }
    if (page !== undefined) { params = params.append('page', page.toString()); }

    if (sortBy) { params = params.append('sortBy', sortBy); }
    if (sortDirection) { params = params.append('sortDirection', sortDirection); }
    if (filterBy) { params = params.append('filterBy', filterBy); }

    return this.http.get<VWABackendResponse>(url, { params }).pipe(
      catchError(error => this.handleError(error)),
      map((resp: VWABackendResponse) => {
        return { pvcs: resp.pvcs, totalCount: resp.totalCount || 0 };
      }),
    );
  }

  private getPVCsAllNamespaces(
    namespaces: string[],
  ): Observable<VWAGetPVCsResponse> {
    // Note: server pagination/sorting is not supported across all namespaces
    // Therefore we will do an un-paginated request and return mock totalCount
    const getPVCsArray = (ns: string): Observable<PVCResponseObject[]> =>
      this.getNamespacedPVCs(ns).pipe(map(r => r.pvcs));

    return this.getObjectsAllNamespaces(
      getPVCsArray,
      namespaces,
    ).pipe(
      map(pvcs => {
        return { pvcs, totalCount: pvcs.length };
      })
    );
  }

  public getPVCs(
    ns: string | string[],
    limit?: number,
    page?: number,
    sortBy?: string,
    sortDirection?: string,
    filterBy?: string,
  ): Observable<VWAGetPVCsResponse> {
    if (!Array.isArray(ns)) {
      return this.getNamespacedPVCs(ns, limit, page, sortBy, sortDirection, filterBy);
    }

    return this.getPVCsAllNamespaces(ns);
  }

  public getPVC(
    namespace: string,
    pvcName: string,
  ): Observable<V1PersistentVolumeClaim> {
    const url = `api/namespaces/${namespace}/pvcs/${pvcName}`;

    return this.http.get<VWABackendResponse>(url).pipe(
      catchError(error => this.handleError(error)),
      map((resp: VWABackendResponse) => resp.pvc),
    );
  }

  public getPVCEvents(pvc: V1PersistentVolumeClaim): Observable<EventObject[]> {
    const namespace = pvc.metadata.namespace;
    const pvcName = pvc.metadata.name;
    const url = `api/namespaces/${namespace}/pvcs/${pvcName}/events`;

    return this.http.get<VWABackendResponse>(url).pipe(
      catchError(error => this.handleError(error)),
      map((resp: VWABackendResponse) => resp.events),
    );
  }

  public getPodsUsingPVC(pvc: V1PersistentVolumeClaim): Observable<V1Pod[]> {
    const namespace = pvc.metadata.namespace;
    const pvcName = pvc.metadata.name;
    const url = `api/namespaces/${namespace}/pvcs/${pvcName}/pods`;

    return this.http.get<VWABackendResponse>(url).pipe(
      catchError(error => this.handleError(error)),
      map((resp: VWABackendResponse) => resp.pods),
    );
  }

  // POST
  public createViewer(namespace: string, viewer: string) {
    const url = `api/namespaces/${namespace}/viewers`;

    return this.http
      .post<VWABackendResponse>(url, { name: viewer })
      .pipe(catchError(error => this.handleError(error)));
  }

  public createPVC(namespace: string, pvc: PVCPostObject) {
    const url = `api/namespaces/${namespace}/pvcs`;

    return this.http
      .post<VWABackendResponse>(url, pvc)
      .pipe(catchError(error => this.handleError(error)));
  }

  // DELETE
  public deletePVC(namespace: string, pvc: string) {
    const url = `api/namespaces/${namespace}/pvcs/${pvc}`;

    return this.http
      .delete<VWABackendResponse>(url)
      .pipe(catchError(error => this.handleError(error, false)));
  }

  public deleteViewer(namespace: string, pvc: string) {
    const url = `api/namespaces/${namespace}/viewers/${pvc}`;

    return this.http
      .delete<VWABackendResponse>(url)
      .pipe(catchError(error => this.handleError(error, false)));
  }
}
