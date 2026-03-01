import { ChangeDetectorRef, Component, OnInit, OnDestroy } from '@angular/core';
import { environment } from '@app/environment';
import {
  NamespaceService,
  ActionEvent,
  STATUS_TYPE,
  ConfirmDialogService,
  SnackBarService,
  DIALOG_RESP,
  SnackType,
  ToolbarButton,
  PollerService,
  DashboardState,
  SnackBarConfig,
} from 'kubeflow';
import { JWABackendService } from 'src/app/services/backend.service';
import { Subject, Subscription } from 'rxjs';
import { debounceTime } from 'rxjs/operators';
import { PageEvent } from '@angular/material/paginator';
import { Sort } from '@angular/material/sort';
import { defaultConfig } from './config';
import { NotebookResponseObject, NotebookProcessedObject } from 'src/app/types';
import { Router } from '@angular/router';
import { ActionsService } from 'src/app/services/actions.service';

@Component({
  standalone: false,
  selector: 'app-index-default',
  templateUrl: './index-default.component.html',
  styleUrls: ['./index-default.component.scss'],
})
export class IndexDefaultComponent implements OnInit, OnDestroy {
  env = environment;

  nsSub = new Subscription();
  pollSub = new Subscription();

  currNamespace: string | string[];
  config = defaultConfig;
  processedData: NotebookProcessedObject[] = [];
  dataLoaded = false;
  dashboardDisconnectedState = DashboardState.Disconnected;

  // Server Pagination State
  totalItems = 0;
  pageSize = 10;
  pageIndex = 0;
  sortActive = 'name';
  sortDirection = 'asc';
  filterValue = '';
  private filterSubject = new Subject<string>();
  private filterSub = new Subscription();

  get isServerPagination(): boolean {
    return this.currNamespace !== undefined && !Array.isArray(this.currNamespace);
  }

  private newNotebookButton = new ToolbarButton({
    text: $localize`New Notebook`,
    icon: 'add',
    stroked: true,
    fn: () => {
      this.router.navigate(['/new']);
    },
  });

  buttons: ToolbarButton[] = [this.newNotebookButton];

  constructor(
    public ns: NamespaceService,
    public backend: JWABackendService,
    public confirmDialog: ConfirmDialogService,
    public snackBar: SnackBarService,
    public router: Router,
    public poller: PollerService,
    public actions: ActionsService,
    private cdr: ChangeDetectorRef,
  ) {}

  ngOnInit(): void {
    // Reset the poller whenever the selected namespace changes
    this.nsSub = this.ns.getSelectedNamespace2().subscribe(ns => {
      this.currNamespace = ns;
      this.dataLoaded = false;
      this.poll(ns);
      this.newNotebookButton.namespaceChanged(ns, $localize`Notebook`);
    });

    this.filterSub = this.filterSubject.pipe(debounceTime(300)).subscribe(val => {
      this.filterValue = val;
      this.pageIndex = 0;
      this.poll(this.currNamespace);
    });
  }

  ngOnDestroy() {
    this.nsSub.unsubscribe();
    this.pollSub.unsubscribe();
    this.filterSub.unsubscribe();
  }

  public poll(ns: string | string[]) {
    this.pollSub.unsubscribe();
    this.processedData = [];

    const request = this.backend.getNotebooks(
      ns,
      this.pageSize,
      this.pageIndex,
      this.sortActive,
      this.sortDirection,
      this.filterValue
    );

    this.pollSub = this.poller.exponential(request).subscribe(resp => {
      this.processedData = this.processIncomingData(resp.notebooks);
      this.totalItems = resp.totalCount;
      this.dataLoaded = true;
      this.cdr.detectChanges();
    });
  }

  // Event handling functions
  reactToAction(a: ActionEvent) {
    switch (a.action) {
      case 'delete':
        this.deleteNotebookClicked(a.data);
        break;
      case 'connect':
        this.connectClicked(a.data);
        break;
      case 'start-stop':
        this.startStopClicked(a.data);
        break;
      case 'name:link':
        if (a.data.status.phase === STATUS_TYPE.TERMINATING) {
          a.event.stopPropagation();
          a.event.preventDefault();
          const config: SnackBarConfig = {
            data: {
              msg: 'Notebook is being deleted, cannot show details.',
              snackType: SnackType.Info,
            },
            duration: 4000,
          };
          this.snackBar.open(config);
          return;
        }
        break;
    }
  }

  onPageChange(event: PageEvent) {
    this.pageSize = event.pageSize;
    this.pageIndex = event.pageIndex;
    this.poll(this.currNamespace);
  }

  onSortChange(event: Sort) {
    this.sortActive = event.active;
    this.sortDirection = event.direction;
    this.poll(this.currNamespace);
  }

  onFilterChange(event: string) {
    this.filterSubject.next(event);
  }

  deleteNotebookClicked(notebook: NotebookProcessedObject) {
    this.actions
      .deleteNotebook(notebook.namespace, notebook.name)
      .subscribe(result => {
        if (result !== DIALOG_RESP.ACCEPT) {
          return;
        }

        notebook.status.phase = STATUS_TYPE.TERMINATING;
        notebook.status.message = 'Preparing to delete the Notebook.';
        this.updateNotebookFields(notebook);
      });
  }

  public connectClicked(notebook: NotebookProcessedObject) {
    this.actions.connectToNotebook(notebook.namespace, notebook.name);
  }

  public startStopClicked(notebook: NotebookProcessedObject) {
    if (notebook.status.phase === STATUS_TYPE.STOPPED) {
      this.startNotebook(notebook);
    } else {
      this.stopNotebook(notebook);
    }
  }

  public startNotebook(notebook: NotebookProcessedObject) {
    this.actions
      .startNotebook(notebook.namespace, notebook.name)
      .subscribe(_ => {
        notebook.status.phase = STATUS_TYPE.WAITING;
        notebook.status.message = 'Starting the Notebook Server.';
        this.updateNotebookFields(notebook);
      });
  }

  public stopNotebook(notebook: NotebookProcessedObject) {
    this.actions
      .stopNotebook(notebook.namespace, notebook.name)
      .subscribe(result => {
        if (result !== DIALOG_RESP.ACCEPT) {
          return;
        }

        notebook.status.phase = STATUS_TYPE.WAITING;
        notebook.status.message = 'Preparing to stop the Notebook Server.';
        this.updateNotebookFields(notebook);
      });
  }

  // Data processing functions
  updateNotebookFields(notebook: NotebookProcessedObject) {
    notebook.deleteAction = this.processDeletionActionStatus(notebook);
    notebook.connectAction = this.processConnectActionStatus(notebook);
    notebook.startStopAction = this.processStartStopActionStatus(notebook);
    notebook.link = {
      text: notebook.name,
      url: `/notebook/details/${notebook.namespace}/${notebook.name}`,
    };
  }

  processIncomingData(notebooks: NotebookResponseObject[]) {
    const notebooksCopy = JSON.parse(
      JSON.stringify(notebooks),
    ) as NotebookProcessedObject[];

    for (const nb of notebooksCopy) {
      this.updateNotebookFields(nb);
    }
    return notebooksCopy;
  }

  // Action handling functions
  processDeletionActionStatus(notebook: NotebookProcessedObject) {
    if (notebook.status.phase !== STATUS_TYPE.TERMINATING) {
      return STATUS_TYPE.READY;
    }

    return STATUS_TYPE.TERMINATING;
  }

  processStartStopActionStatus(notebook: NotebookProcessedObject) {
    // Stop button
    if (notebook.status.phase === STATUS_TYPE.READY) {
      return STATUS_TYPE.UNINITIALIZED;
    }

    // Start button
    if (notebook.status.phase === STATUS_TYPE.STOPPED) {
      return STATUS_TYPE.READY;
    }

    // If it is terminating, then the action should be disabled
    if (notebook.status.phase === STATUS_TYPE.TERMINATING) {
      return STATUS_TYPE.UNAVAILABLE;
    }

    // If the Notebook is not Terminating, then always allow the stop action
    return STATUS_TYPE.UNINITIALIZED;
  }

  processConnectActionStatus(notebook: NotebookProcessedObject) {
    if (notebook.status.phase !== STATUS_TYPE.READY) {
      return STATUS_TYPE.UNAVAILABLE;
    }

    return STATUS_TYPE.READY;
  }

  public notebookTrackByFn(index: number, notebook: NotebookProcessedObject) {
    return `${notebook.name}/${notebook.image}`;
  }
}
