import { Injectable } from '@angular/core';
import { BackendService, SnackBarService } from 'kubeflow';
import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import {
  NotebookResponseObject,
  NotebookRawObject,
  JWABackendResponse,
  Config,
  PodDefault,
  NotebookFormObject,
  NotebookProcessedObject,
  PvcResponseObject,
} from '../types';
import { V1Pod } from '@kubernetes/client-node';
import { EventObject } from '../types/event';
import { Router } from '@angular/router';
@Injectable({
  providedIn: 'root',
})
export class JWABackendService extends BackendService {
  constructor(public http: HttpClient, public snackBar: SnackBarService) {
    super(http, snackBar);
  }

  // GET
  private getNotebooksSingleNamespace(
    namespace: string,
    limit?: number,
    page?: number,
    sortBy?: string,
    sortDirection?: string,
    filterBy?: string,
  ): Observable<{ notebooks: NotebookResponseObject[]; totalCount: number }> {
    const url = `api/namespaces/${namespace}/notebooks`;
    let params = new HttpParams();
    if (limit !== undefined) { params = params.append('limit', limit.toString()); }
    if (page !== undefined) { params = params.append('page', page.toString()); }
    if (sortBy) { params = params.append('sortBy', sortBy); }
    if (sortDirection) { params = params.append('sortDirection', sortDirection); }
    if (filterBy) { params = params.append('filterBy', filterBy); }

    return this.http.get<JWABackendResponse>(url, { params }).pipe(
      catchError(error => { throw this.handleError(error)}),
      map((resp: JWABackendResponse) => ({ notebooks: resp.notebooks, totalCount: resp.totalCount })),
    );
  }

  private getNotebooksAllNamespaces(
    namespaces: string[],
  ): Observable<NotebookResponseObject[]> {
    return this.getObjectsAllNamespaces(
      (ns) => this.getNotebooksSingleNamespace(ns).pipe(
        map(res => res.notebooks)
      ),
      namespaces,
    );
  }

  public getNotebooks(
    ns: string | string[],
    limit?: number,
    page?: number,
    sortBy?: string,
    sortDirection?: string,
    filterBy?: string,
  ): Observable<{ notebooks: NotebookResponseObject[]; totalCount: number }> {
    if (Array.isArray(ns)) {
      return this.getNotebooksAllNamespaces(ns).pipe(
        map(notebooks => ({ notebooks, totalCount: notebooks.length }))
      );
    }

    return this.getNotebooksSingleNamespace(ns, limit, page, sortBy, sortDirection, filterBy);
  }

  public getNotebook(
    namespace: string,
    notebookName: string,
  ): Observable<NotebookRawObject> {
    const url = `api/namespaces/${namespace}/notebooks/${notebookName}`;

    return this.http.get<JWABackendResponse>(url).pipe(
      catchError(error => { throw this.handleError(error)}),
      map((resp: JWABackendResponse) => resp.notebook),
    );
  }

  public getNotebookPod(notebook: NotebookRawObject): Observable<V1Pod> {
    const namespace = notebook.metadata.namespace;
    const notebookName = notebook.metadata.name;
    const url = `api/namespaces/${namespace}/notebooks/${notebookName}/pod`;

    return this.http.get<JWABackendResponse>(url).pipe(
      catchError(error => { throw this.handleErrorExtended(error, [404])}),
      map((resp: JWABackendResponse) => resp.pod),
    );
  }

  public getPodLogs(pod: V1Pod): Observable<string[]> {
    const namespace = pod.metadata.namespace;
    const notebookName = pod.metadata.labels['notebook-name'];
    const podName = pod.metadata.name;
    const url = `api/namespaces/${namespace}/notebooks/${notebookName}/pod/${podName}/logs`;
    return this.http.get<JWABackendResponse>(url).pipe(
      catchError(error => { throw this.handleErrorExtended(error, [404, 400])}),
      map((resp: JWABackendResponse) => resp.logs),
    );
  }

  public getNotebookEvents(
    notebook: NotebookRawObject,
  ): Observable<EventObject[]> {
    const namespace = notebook.metadata.namespace;
    const notebookName = notebook.metadata.name;
    const url = `api/namespaces/${namespace}/notebooks/${notebookName}/events`;

    return this.http.get<JWABackendResponse>(url).pipe(
      catchError(error => { throw this.handleErrorExtended(error, [404])}),
      map((resp: JWABackendResponse) => resp.events),
    );
  }

  public getConfig(): Observable<Config> {
    const url = `api/config`;

    return this.http.get<JWABackendResponse>(url).pipe(
      catchError(error => { throw this.handleError(error)}),
      map(data => data.config),
    );
  }

  public getVolumes(ns: string): Observable<PvcResponseObject[]> {
    // Get existing PVCs in a namespace
    const url = `api/namespaces/${ns}/pvcs`;

    return this.http.get<JWABackendResponse>(url).pipe(
      catchError(error => { throw this.handleError(error)}),
      map(data => data.pvcs),
    );
  }

  public getPodDefaults(ns: string): Observable<PodDefault[]> {
    // Get existing PodDefaults in a namespace
    const url = `api/namespaces/${ns}/poddefaults`;

    return this.http.get<JWABackendResponse>(url).pipe(
      catchError(error => { throw this.handleError(error)}),
      map(data => data.poddefaults),
    );
  }

  public getGPUVendors(): Observable<string[]> {
    // Get installed GPU vendors
    const url = `api/gpus`;

    return this.http.get<JWABackendResponse>(url).pipe(
      catchError(error => { throw this.handleError(error)}),
      map(data => data.vendors),
    );
  }

  // POST
  public createNotebook(notebook: NotebookFormObject): Observable<string> {
    const url = `api/namespaces/${notebook.namespace}/notebooks`;

    return this.http.post<JWABackendResponse>(url, notebook).pipe(
      catchError(error => { throw this.handleError(error)}),
      map(_ => 'posted'),
    );
  }

  // PATCH
  public startNotebook(namespace: string, name: string): Observable<string> {
    const url = `api/namespaces/${namespace}/notebooks/${name}`;

    return this.http.patch<JWABackendResponse>(url, { stopped: false }).pipe(
      catchError(error => { throw this.handleError(error)}),
      map(_ => 'started'),
    );
  }

  public stopNotebook(namespace: string, name: string): Observable<string> {
    const url = `api/namespaces/${namespace}/notebooks/${name}`;

    return this.http.patch<JWABackendResponse>(url, { stopped: true }).pipe(
      catchError(error => { throw this.handleError(error, false)}),
      map(_ => 'stopped'),
    );
  }

  // DELETE
  public deleteNotebook(namespace: string, name: string) {
    const url = `api/namespaces/${namespace}/notebooks/${name}`;

    return this.http
      .delete<JWABackendResponse>(url)
      .pipe(catchError(error => { throw this.handleError(error, false)}));
  }

  // ---------------------------Error Handling---------------------------------

  public handleErrorExtended(
    error: HttpErrorResponse | ErrorEvent | string,
    codes: number[] = [],
  ): Observable<never> {
    if (
      error instanceof HttpErrorResponse &&
      codes.includes(error.error.status)
    ) {
      // Error code is expected so we do not open a snackBar dialog
      return this.handleError(error, false);
    } else {
      return this.handleError(error);
    }
  }

  // Override common service's getErrorMessage
  // in order to incldue the error.status in error message
  public getErrorMessage(
    error: HttpErrorResponse | ErrorEvent | string,
  ): string {
    if (typeof error === 'string') {
      return error;
    }

    if (error instanceof HttpErrorResponse) {
      if (this.getBackendErrorLog(error) !== undefined) {
        return `[${error.status}] ${this.getBackendErrorLog(error)}`;
      }

      return `${error.status}: ${error.message}`;
    }

    if (error instanceof ErrorEvent) {
      return error.message;
    }

    return `Unexpected error encountered`;
  }
}
